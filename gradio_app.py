import gradio as gr
from pathlib import Path
from scripts.inference import main
from omegaconf import OmegaConf
import argparse
from datetime import datetime

CONFIG_PATH = Path("configs/unet/stage2.yaml")
GRADIO_CONFIG = Path("config.yaml")
CHECKPOINT_PATH = Path("checkpoints/latentsync_unet.pt")

gradio_config = OmegaConf.load(GRADIO_CONFIG)

def process_video(
    video_path,
    audio_path,
    guidance_scale,
    inference_steps,
    seed,
):
    # Create the temp directory if it doesn't exist
    output_dir = Path("./temp")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert paths to absolute Path objects and normalize them
    video_file_path = Path(video_path)
    video_path = video_file_path.absolute().as_posix()
    audio_path = Path(audio_path).absolute().as_posix()

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Set the output path for the processed video
    output_path = str(output_dir / f"{video_file_path.stem}_{current_time}.mp4")  # Change the filename as needed

    config = OmegaConf.load(CONFIG_PATH)

    config["run"].update(
        {
            "guidance_scale": guidance_scale,
            "inference_steps": inference_steps,
        }
    )

    # Parse the arguments
    args = create_args(video_path, audio_path, output_path, inference_steps, guidance_scale, seed)

    try:
        result = main(
            config=config,
            args=args,
        )
        print("Processing completed successfully.")
        return output_path  # Ensure the output path is returned
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise gr.Error(f"Error during processing: {str(e)}")


def create_args(
    video_path: str, audio_path: str, output_path: str, inference_steps: int, guidance_scale: float, seed: int
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inference_ckpt_path", type=str, required=True)
    parser.add_argument("--video_path", type=str, required=True)
    parser.add_argument("--audio_path", type=str, required=True)
    parser.add_argument("--video_out_path", type=str, required=True)
    parser.add_argument("--inference_steps", type=int, default=20)
    parser.add_argument("--guidance_scale", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1247)

    return parser.parse_args(
        [
            "--inference_ckpt_path",
            CHECKPOINT_PATH.absolute().as_posix(),
            "--video_path",
            video_path,
            "--audio_path",
            audio_path,
            "--video_out_path",
            output_path,
            "--inference_steps",
            str(inference_steps),
            "--guidance_scale",
            str(guidance_scale),
            "--seed",
            str(seed),
        ]
    )


# Create Gradio interface
with gr.Blocks(title="LatentSync demo") as demo:
    gr.Markdown(
    """
    <h1 align="center">LatentSync</h1>

    <div style="display:flex;justify-content:center;column-gap:4px;">
        <a href="https://github.com/bytedance/LatentSync">
            <img src='https://img.shields.io/badge/GitHub-Repo-blue'>
        </a> 
        <a href="https://arxiv.org/abs/2412.09262">
            <img src='https://img.shields.io/badge/arXiv-Paper-red'>
        </a>
    </div>
    """
    )

    with gr.Row():
        with gr.Column():
            video_input = gr.Video(label="Input Video")
            audio_input = gr.Audio(label="Input Audio", type="filepath")

            with gr.Row():
                guidance_scale = gr.Slider(
                    minimum=1.0,
                    maximum=3.0,
                    value=2.0,
                    step=0.5,
                    label="Guidance Scale",
                )
                inference_steps = gr.Slider(minimum=10, maximum=50, value=20, step=1, label="Inference Steps")

            with gr.Row():
                seed = gr.Number(value=1247, label="Random Seed", precision=0)

            process_btn = gr.Button("Process Video")

        with gr.Column():
            video_output = gr.Video(label="Output Video")

            gr.Examples(
                examples=[
                    ["assets/demo1_video.mp4", "assets/demo1_audio.wav"],
                    ["assets/demo2_video.mp4", "assets/demo2_audio.wav"],
                    ["assets/demo3_video.mp4", "assets/demo3_audio.wav"],
                ],
                inputs=[video_input, audio_input],
            )

    process_btn.click(
        fn=process_video,
        inputs=[
            video_input,
            audio_input,
            guidance_scale,
            inference_steps,
            seed,
        ],
        outputs=video_output,
    )

if __name__ == "__main__":
    demo.launch(
        server_name=gradio_config.server_name,
        server_port=gradio_config.server_port,
        auth=tuple(gradio_config.auth)
    )
