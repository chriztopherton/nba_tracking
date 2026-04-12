"""
A module for reading and writing video files.

This module provides utility functions to load video frames into memory and save
processed frames back to video files, with support for common video formats.
"""

import cv2
import os


def get_video_properties(video_path):
    """
    Read basic metadata from a video file (fps, dimensions, frame count).

    Returns:
        dict: Keys fps, frame_count, width, height. fps defaults to 24.0 if unknown.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"fps": 24.0, "frame_count": 0, "width": 0, "height": 0}
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    if fps <= 1e-6:
        fps = 24.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return {"fps": fps, "frame_count": frame_count, "width": width, "height": height}

def read_video(video_path):
    """
    Read all frames from a video file into memory.

    Args:
        video_path (str): Path to the input video file.

    Returns:
        list: List of video frames as numpy arrays.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        cap.release()
        raise ValueError(
            f"Could not open video (invalid path, format, or codec): {video_path}"
        )

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    if not frames:
        raise ValueError(
            f"No frames decoded from video (empty or unreadable file): {video_path}"
        )
    return frames

def save_video(ouput_video_frames,output_video_path):
    """
    Save a sequence of frames as a video file.

    Creates necessary directories if they don't exist. Uses MPEG-4 Part 2 (.mp4/.mov)
    for broad macOS QuickTime compatibility; uses XVID only for .avi paths.

    Args:
        ouput_video_frames (list): List of frames to save.
        output_video_path (str): Path where the video should be saved.
    """
    if not ouput_video_frames:
        raise ValueError("No frames to save; nothing was produced (check input video path).")

    # If folder doesn't exist, create it
    out_dir = os.path.dirname(output_video_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    ext = os.path.splitext(output_video_path)[1].lower()
    if ext == ".avi":
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
    else:
        # QuickTime plays .mp4 with mp4v reliably; default for unknown extensions.
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(output_video_path, fourcc, 24, (ouput_video_frames[0].shape[1], ouput_video_frames[0].shape[0]))
    for frame in ouput_video_frames:
        out.write(frame)
    out.release()