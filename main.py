import asyncio
import aiofiles
import aiohttp
import os


class OlympusCameraImage:
    def __init__(self, _url, _camera_connection_limits=2):
        """
        :param _url:
        :param _camera_connection_limits: my camera can only handle 2 connections at a time
        """
        self.__url = _url
        self.__camera_connection_limits = _camera_connection_limits

    def download(self, start, end, _save_folder):
        self.__create_folder(_save_folder)
        image_urls_chunk = self.__create_urls_chunk(start, end)
        self.__asyncio_download(image_urls_chunk, _save_folder)

    def __create_folder(self, save_folder):
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

    def __create_urls_chunk(self, start, end):
        image_urls = [self.__url(number) for number in range(start, end + 1)]
        return [image_urls[i:i + self.__camera_connection_limits] for i in
                range(0, len(image_urls), self.__camera_connection_limits)]

    def __asyncio_download(self, image_urls_chunk, save_folder):
        for chunk in image_urls_chunk:
            asyncio.run(self.__main(chunk, save_folder))

    async def __main(self, image_urls, save_folder):
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(self.__download_image(session, url, save_folder)) for url in image_urls]
            await asyncio.gather(*tasks)

    async def __download_image(self, session, url, save_folder):
        async with session.get(url) as response:
            if response.status == 200:
                file_name = os.path.join(save_folder, url.split('/')[-1])
                async with aiofiles.open(file_name, 'wb') as f:
                    content = await response.read()
                    await f.write(content)
                print(f"Success download!: {file_name}")
            else:
                print(f"No Image: {url}")


if __name__ == '__main__':
    save_folder = 'images'
    url = lambda number: f"http://192.168.0.10/DCIM/100OLYMP/P{number}.JPG"
    start_number = 1010760  # 2160903
    end_number = 1010898  # 2161191

    olympus = OlympusCameraImage(url)
    olympus.download(start_number, end_number, save_folder)
