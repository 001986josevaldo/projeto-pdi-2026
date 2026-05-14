import os
import subprocess


class VideoConverter:

    @staticmethod
    def convert_to_h264(input_video, delete_original=False):

        base, _ = os.path.splitext(input_video)

        output_video = base + ".mp4"

        command = [
            "ffmpeg",
            "-y",
            "-i", input_video,
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            output_video
        ]

        try:

            print("🎬 Convertendo vídeo...")

            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if delete_original and os.path.exists(input_video):
                os.remove(input_video)

            print("✅ Conversão concluída.")

            return output_video

        except Exception as e:

            print(f"❌ Erro: {e}")

            return None