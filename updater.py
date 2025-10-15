import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import time
from packaging.version import parse
from tqdm import tqdm
import requests
import psutil
import urllib.request
from urllib.request import urlopen
from urllib.error import URLError
from utils.color import red, green
from utils.logger.logger import Logger


class Updater:
    """애플리케이션 업데이터, 최신 버전의 애플리케이션을 확인, 다운로드, 압축 해제 및 설치하는 역할을 합니다."""

    def __init__(self, logger: Logger, download_url=None, file_name=None):
        self.logger = logger
        self.process_names = ["March7th Assistant.exe", "March7th Launcher.exe", "flet.exe", "gui.exe"]
        self.api_urls = [
            "https://api.github.com/repos/moesnow/March7thAssistant/releases/latest",
            "https://github.kotori.top/https://api.github.com/repos/moesnow/March7thAssistant/releases/latest",
        ]
        self.temp_path = os.path.abspath("./temp")
        os.makedirs(self.temp_path, exist_ok=True)
        self.download_url = download_url
        self.file_name = file_name
        self.cover_folder_path = os.path.abspath("./")
        self.exe_path = os.path.abspath("./assets/binary/7za.exe")
        self.aria2_path = os.path.abspath("./assets/binary/aria2c.exe")
        self.delete_folder_path = os.path.join("./3rdparty/Fhoe-Rail", "map")

        self.logger.hr("다운로드 링크 가져오기", 0)
        if download_url is None:
            self.download_url = self.get_download_url()
            self.logger.info(f"다운로드 링크: {green(self.download_url)}")
            self.logger.hr("완료", 2)
            input("업데이트를 시작하려면 엔터 키를 누르세요")
        else:
            self.logger.info(f"다운로드 링크: {green(self.download_url)}")
            self.logger.hr("완료", 2)
        self.download_file_path = os.path.join(self.temp_path, self.file_name)
        self.extract_folder_path = os.path.join(self.temp_path, self.file_name.rsplit(".", 1)[0])

    def get_download_url(self):
        """업데이트를 확인하고 다운로드 URL을 가져옵니다."""
        self.logger.info("업데이트 확인 시작")
        fastest_mirror = self.find_fastest_mirror(self.api_urls)
        try:
            with urlopen(fastest_mirror, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return self.process_release_data(data)
        except URLError as e:
            self.logger.error(f"업데이트 확인 실패: {red(e)}")
            input("다시 시도하려면 엔터 키를 누르세요...")
            return self.get_download_url()

    def process_release_data(self, data):
        """릴리스 데이터를 처리하고, 다운로드 URL을 가져와 버전을 비교합니다."""
        version = data["tag_name"]
        download_url = None
        for asset in data["assets"]:
            if "full" in asset["browser_download_url"]:
                download_url = asset["browser_download_url"]
                self.file_name = asset["name"]
                break

        if download_url is None:
            raise Exception("적절한 다운로드 URL을 찾을 수 없습니다")

        self.compare_versions(version)
        return download_url

    def compare_versions(self, version):
        """로컬 버전과 원격 버전을 비교합니다."""
        try:
            with open("./assets/config/version.txt", 'r', encoding='utf-8') as file:
                current_version = file.read().strip()
            if parse(version.lstrip('v')) > parse(current_version.lstrip('v')):
                self.logger.info(f"새 버전 발견: {current_version} ——> {version}")
            else:
                self.logger.info(f"로컬 버전: {current_version}")
                self.logger.info(f"원격 버전: {version}")
                self.logger.info(f"이미 최신 버전입니다")
        except Exception as e:
            self.logger.info(f"로컬 버전 가져오기 실패: {e}")
            self.logger.info(f"최신 버전: {version}")

    def find_fastest_mirror(self, mirror_urls, timeout=5):
        """속도를 측정하여 가장 빠른 미러를 찾습니다."""
        def check_mirror(mirror_url):
            try:
                start_time = time.time()
                response = requests.head(mirror_url, timeout=timeout, allow_redirects=True)
                end_time = time.time()
                if response.status_code == 200:
                    return mirror_url, end_time - start_time
            except Exception:
                pass
            return None, None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_mirror, url) for url in mirror_urls]
            fastest_mirror, _ = min((future.result() for future in concurrent.futures.as_completed(futures)), key=lambda x: (x[1] is not None, x[1]), default=(None, None))

        return fastest_mirror if fastest_mirror else mirror_urls[0]

    def download_with_progress(self):
        """파일을 다운로드하고 진행률 표시줄을 보여줍니다."""
        self.logger.hr("다운로드", 0)
        proxies = urllib.request.getproxies()
        while True:
            try:
                self.logger.info("다운로드 시작...")
                if os.path.exists(self.aria2_path):
                    command = [
                        self.aria2_path,
                        "--disable-ipv6=true",
                        "--dir={}".format(os.path.dirname(self.download_file_path)),
                        "--out={}".format(os.path.basename(self.download_file_path)),
                        self.download_url
                    ]

                    if "github.com" in self.download_url:
                        command.insert(2, "--max-connection-per-server=16")
                        # GitHub 리소스 다운로드 시에만 이어받기를 활성화하여 416 오류 방지
                        if os.path.exists(self.download_file_path):
                            command.insert(2, "--continue=true")
                    # 프록시 설정
                    for scheme, proxy in proxies.items():
                        if scheme in ("http", "https", "ftp"):
                            command.append(f"--{scheme}-proxy={proxy}")
                    subprocess.run(command, check=True)

                else:
                    response = requests.head(self.download_url, allow_redirects=True)
                    response.raise_for_status()
                    file_size = int(response.headers.get('Content-Length', 0))

                    with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                        with requests.get(self.download_url, stream=True) as r:
                            with open(self.download_file_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=1024):
                                    if chunk:
                                        f.write(chunk)
                                        pbar.update(len(chunk))

                self.logger.info(f"다운로드 완료: {green(self.download_file_path)}")
                break

            except Exception as e:
                self.logger.error(f"다운로드 실패: {red('네트워크 연결이 정상인지 확인하거나, 업데이트 소스를 변경한 후 다시 시도하세요.')}")
                input("다시 시도하려면 엔터 키를 누르세요. . .")
        self.logger.hr("완료", 2)

    def extract_file(self):
        """다운로드한 파일의 압축을 해제합니다."""
        self.logger.hr("압축 해제", 0)
        while True:
            try:
                self.logger.info("압축 해제 시작...")
                if os.path.exists(self.exe_path):
                    subprocess.run([self.exe_path, "x", self.download_file_path, f"-o{self.temp_path}", "-aoa"], check=True)
                else:
                    shutil.unpack_archive(self.download_file_path, self.temp_path)
                self.logger.info(f"압축 해제 완료: {green(self.extract_folder_path)}")
                self.logger.hr("완료", 2)
                return True
            except Exception as e:
                self.logger.error(f"압축 해제 실패: {red(e)}")
                self.logger.hr("완료", 2)
                input("다시 다운로드하려면 엔터 키를 누르세요. . .")
                if os.path.exists(self.download_file_path):
                    os.remove(self.download_file_path)
                return False

    def cover_folder(self):
        """최신 버전의 파일로 덮어씁니다."""
        self.logger.hr("덮어쓰기", 0)
        while True:
            try:
                self.logger.info("덮어쓰기 시작...")
                if "full" in self.file_name and os.path.exists(self.delete_folder_path):
                    shutil.rmtree(self.delete_folder_path)
                shutil.copytree(self.extract_folder_path, self.cover_folder_path, dirs_exist_ok=True)
                self.logger.info(f"덮어쓰기 완료: {green(self.cover_folder_path)}")
                break
            except Exception as e:
                self.logger.error(f"덮어쓰기 실패: {red(e)}")
                input("다시 시도하려면 엔터 키를 누르세요. . .")
        self.logger.hr("완료", 2)

    def terminate_processes(self):
        """업데이트 준비를 위해 관련 프로세스를 종료합니다."""
        self.logger.hr("프로세스 종료", 0)
        self.logger.info("프로세스 종료 시작...")
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if proc.info['name'] in self.process_names:
                try:
                    proc.terminate()
                    proc.wait(10)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired, psutil.AccessDenied):
                    pass
        self.logger.info(green("프로세스 종료 완료"))
        self.logger.hr("완료", 2)

    def cleanup(self):
        """다운로드 및 압축 해제된 임시 파일을 정리합니다."""
        self.logger.hr("정리", 0)
        self.logger.info("정리 시작...")
        try:
            os.remove(self.download_file_path)
            self.logger.info(f"정리 완료: {green(self.download_file_path)}")
            shutil.rmtree(self.extract_folder_path)
            self.logger.info(f"정리 완료: {green(self.extract_folder_path)}")
        except Exception as e:
            self.logger.error(f"정리 실패: {e}")
        self.logger.hr("완료", 2)

    def run(self):
        """업데이트 절차를 실행합니다."""
        while True:
            self.download_with_progress()
            if self.extract_file():
                break
        self.terminate_processes()
        self.cover_folder()
        self.cleanup()
        input("엔터 키를 눌러 종료하고 프로그램을 여세요")
        if os.system(f'cmd /c start "" "{os.path.abspath("./March7th Launcher.exe")}"'):
            subprocess.Popen(os.path.abspath("./March7th Launcher.exe"))


def check_temp_dir_and_run():
    """임시 디렉토리를 확인하고 업데이터를 실행합니다."""
    if not getattr(sys, 'frozen', False):
        print("업데이터는 exe로 패키징된 후에만 실행할 수 있습니다")
        sys.exit(1)

    temp_path = os.path.abspath("./temp")
    file_path = sys.argv[0]
    destination_path = os.path.join(temp_path, os.path.basename(file_path))

    if file_path != destination_path:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        if os.path.exists("./Update.exe"):
            os.remove("./Update.exe")
        os.makedirs(temp_path, exist_ok=True)
        shutil.copy(file_path, destination_path)
        args = [destination_path] + sys.argv[1:]
        subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)
        sys.exit(0)

    download_url = sys.argv[1] if len(sys.argv) == 3 else None
    file_name = sys.argv[2] if len(sys.argv) == 3 else None
    logger = Logger()
    updater = Updater(logger, download_url, file_name)
    updater.run()


if __name__ == '__main__':
    check_temp_dir_and_run()