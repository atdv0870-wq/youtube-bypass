import os
import cv2
import numpy as np
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, vfx
import random
import string

# === DESTROY VIDEO FINGERPRINT ===
def corrupt_video_fingerprint(input_path, output_path):
    clip = VideoFileClip(input_path)
    
    # Random speed shift between 98% - 103%
    speed = 0.98 + random.uniform(0, 0.05)
    new_duration = clip.duration / speed

    # Resize slightly + add noise layer
    corrupted = (
        clip.fx(vfx.speedx, speed)
           .fx(vfx.resize, width=clip.w - random.choice([2,4,6]))
           .fx(vfx.color_modulate, hue=(-0.1, 0.1))
    )

    # Export with low CRF (high quality), but altered FPS
    altered_fps = int(clip.fps + random.choice([-1,-2,+1]))
    corrupted.write_videofile(
        output_path,
        fps=altered_fps,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        remove_temp=True,
        threads=4,
        ffmpeg_params=["-crf", "18"]
    )
    print(f"[+] Fingerprint destroyed ? {output_path}")

# === CORRUPT AUDIO SIGNATURE ===
def corrupt_audio(video_path):
    audio = AudioSegment.from_file(video_path)
    
    # Shift pitch ±3%
    semitones = random.uniform(-3, 3)
    new_sample_rate = int(audio.frame_rate * (2.0 ** (semitones / 12.0)))
    
    pitched = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched.export("temp_audio.mp3", format="mp3")

# === RANDOMIZE METADATA ===
def random_title():
    titles = [
        f"My Dad Reacts To WiFi Password {random.randint(100,999)}",
        "Windows XP Startup Sounds ASMR ?",
        "I Recorded My Fridge For 8 Hours...",
        f"How To Draw A Circle #{random.randint(500,999)} Speed Art",
        "Baby Laughing At TCP/IP Packets"
    ]
    return random.choice(titles)

# === FRAGMENT VIDEO INTO SMALL CLIPS ===
def fragment_video(video_path):
    os.makedirs("fragments", exist_ok=True)
    
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    
     # Split into ~15 second clips (~450 frames)
     fragment_duration_frames = int(fps * 15)

     for i in range(0, frame_count // fragment_duration_frames + 1):
         outpath = f"fragments/clip_{i:04d}.mp4"
         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
         writer = cv2.VideoWriter(outpath , fourcc,fps,(int(vidcap.get(3)),int(vidcap.get(4))))

         for _ in range(fragment_duration_frames):
             success,img=vidcap.read()
             if not success:
                 break 
             writer.write(img)

         writer.release()

     print("[+] Video split into unrecognizable garbage.")

if __name__ == "__main__":
     input_movie ="input_movie.mp4"
     temp_output="corrupted_output.mp4"

     corrupt_video_fingerprint(input_movie,temp_output)
     corrupt_audio(temp_output)
     fragment_video(temp_output)

     print(f"[+] Upload Title Suggestion: '{random_title()}'")