import os
import fitz
from io import BytesIO
from PIL import Image
import base64
from gpt_utility import GPTManager
from s3_manager import S3Manager
from enum_utility import Bucket
from decouple import config


BASE_TRANSCRIPT_PATH = config('BASE_TRANSCRIPT_PATH')
api_key = config('OPEN_AI_API_KEY')
BASE_PDF_PATH = config('BASE_PDF_PATH')
BASE_TEXT_PATH = config('BASE_TEXT_PATH')



class PDFToTextUtilityManager:

    def     __init__(self, s3_pdf_file_path):

        self.gpt_manager = GPTManager()
        self.s3_file_manager = S3Manager()
        self.s3_pdf_file_path = s3_pdf_file_path
        self.local_text_path = f"{config('BASE_TEXT_PATH')}{s3_pdf_file_path.split("/")[-1].split(".")[0]}.txt"
        self.local_pdf_path = f"{config('BASE_PDF_PATH')}{s3_pdf_file_path.split("/")[-1]}"

    def encode_image_from_bytes(self, image_bytes):
        return base64.b64encode(image_bytes).decode('utf-8')

    def pdf_as_base64_images(self, zoom=2, resize_factor=0.5, quality=85):
        try:
            document = fitz.open(self.local_pdf_path)
            base64_images = []
            # output_directory = f"{config('BASE_PDF_PATH')}"

            for page_num in range(document.page_count):
                page = document.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))

                # Convert pixmap to an image
                image = Image.open(BytesIO(pix.tobytes()))

                # Resize image
                new_size = (int(image.width * resize_factor), int(image.height * resize_factor))
                resized_image = image.resize(new_size, Image.Resampling.LANCZOS)

                # image_file_path = os.path.join(output_directory, f"page_{page_num + 1}_resized.png")
                # resized_image.save(image_file_path, format="PNG", quality=quality, optimize=True)

                # Save image to bytes buffer
                buffer = BytesIO()
                resized_image.save(buffer, format="PNG", quality=quality, optimize=True)
                buffer.seek(0)

                # Encode image to base64
                base64_resized_image = self.encode_image_from_bytes(buffer.read())
                base64_images.append(base64_resized_image)

                # base64_file_path = os.path.join(output_directory, f"page_{page_num + 1}.txt")
                # with open(base64_file_path, "w") as base64_file:
                #     base64_file.write(base64_resized_image)
            return base64_images
        except Exception as err:
            print(err)

    def create_upload_path(self):
        path_parts = self.s3_pdf_file_path.split("/")
        # upload_path = f"{path_parts[0]}/text/{path_parts[2]}/{path_parts[3]}/{path_parts[4]}/{self.s3_pdf_file_path.split("/")[-1].split(".")[0]}.txt"
        upload_path = f"ai_live_query_resolution/handouts/{self.s3_pdf_file_path.split("/")[-1].split(".")[0]}.txt"
        return upload_path

    def delete_files(self):
        if os.path.exists(self.local_pdf_path):
            os.remove(self.local_pdf_path)
            print(f"{self.local_pdf_path} deleted...")

        if os.path.exists(self.local_text_path):
            os.remove(self.local_text_path)
            print(f"{self.local_text_path} deleted...")

    def pdf_processing(self):
        try:
            images = self.pdf_as_base64_images()

            print(f"total number of pages for {self.s3_pdf_file_path.split("/")[-1]}: {len(images)}")

            book = []
            for image in images:
                gpt_manager = self.gpt_manager
                gpt_response = gpt_manager.image_to_text(image)
                book.append(gpt_response['choices'][0]['message']['content'])

            book_str = "\n\n".join(book)
            with open(self.local_text_path, "w", encoding="utf-8") as file:
                file.write(book_str)

            s3_upload_path = self.create_upload_path()
            self.s3_file_manager.upload_file_on_s3(
                local_file_path=self.local_text_path,
                s3_upload_path=s3_upload_path,
                bucket= Bucket.RESOURCES_BUCKET.value
            )

            print(f"processing complete for {self.s3_pdf_file_path.split("/")[-1]}")
            self.delete_files()
            return book_str
        except Exception as err:
            return err


