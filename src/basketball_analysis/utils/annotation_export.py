"""
Export per-frame annotations as CSV tables for film analysis and downstream tooling.
"""

import os

import pandas as pd


def export_annotation_tables(
    export_dir,
    ball_tracks,
    tactical_ball_positions,
    tactical_view_width,
    tactical_view_height,
    court_width_m,
    court_height_m,
    player_assignment,
    ball_possession,
    passes,
    interceptions,
    tactical_player_positions,
    player_distances_per_frame,
    player_speed_per_frame,
    fps,
):
    """
    Write CSV tables next to the output video.

    Files:
      - per_frame.csv — time, ball pixel/tactical position, possession, pass/interception flags
      - players_long.csv — one row per (frame, player) with tactical coords and motion stats
    """
    os.makedirs(export_dir, exist_ok=True)

    n = len(ball_possession)
    if n == 0:
        return

    def px_to_m(tx, ty):
        if tx is None or ty is None:
            return None, None
        mx = float(tx) / tactical_view_width * court_width_m
        my = float(ty) / tactical_view_height * court_height_m
        return mx, my

    per_frame_rows = []
    for f in range(n):
        t_sec = f / fps if fps and fps > 0 else float(f)

        ball_row = ball_tracks[f].get(1, {}) if f < len(ball_tracks) else {}
        bbox = ball_row.get("bbox") if ball_row else None
        if bbox and len(bbox) >= 4:
            x1, y1, x2, y2 = bbox[0], bbox[1], bbox[2], bbox[3]
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
        else:
            x1 = y1 = x2 = y2 = cx = cy = None

        tac = tactical_ball_positions[f] if f < len(tactical_ball_positions) else None
        if tac is not None:
            tx, ty = tac[0], tac[1]
            mx, my = px_to_m(tx, ty)
            court_ok = True
        else:
            tx = ty = mx = my = None
            court_ok = False

        poss_pid = ball_possession[f] if f < len(ball_possession) else -1
        assign = player_assignment[f] if f < len(player_assignment) else {}
        poss_team = assign.get(poss_pid, -1) if poss_pid != -1 else -1

        pass_v = passes[f] if f < len(passes) else -1
        int_v = interceptions[f] if f < len(interceptions) else -1

        per_frame_rows.append(
            {
                "frame_index": f,
                "time_sec": round(t_sec, 6),
                "ball_bbox_x1": x1,
                "ball_bbox_y1": y1,
                "ball_bbox_x2": x2,
                "ball_bbox_y2": y2,
                "ball_center_px_x": cx,
                "ball_center_px_y": cy,
                "ball_tactical_px_x": tx,
                "ball_tactical_px_y": ty,
                "ball_tactical_m_x": mx,
                "ball_tactical_m_y": my,
                "court_projection_ok": court_ok,
                "possession_player_id": poss_pid,
                "possession_team": poss_team,
                "pass_team": pass_v,
                "interception_team": int_v,
            }
        )

    df_frame = pd.DataFrame(per_frame_rows)
    df_frame.to_csv(os.path.join(export_dir, "per_frame.csv"), index=False)

    player_rows = []
    for f in range(n):
        assign = player_assignment[f] if f < len(player_assignment) else {}
        tact = tactical_player_positions[f] if f < len(tactical_player_positions) else {}
        dists = player_distances_per_frame[f] if f < len(player_distances_per_frame) else {}
        speeds = player_speed_per_frame[f] if f < len(player_speed_per_frame) else {}
        t_sec = f / fps if fps and fps > 0 else float(f)

        for player_id, pos in tact.items():
            tx, ty = float(pos[0]), float(pos[1])
            mx, my = px_to_m(tx, ty)
            player_rows.append(
                {
                    "frame_index": f,
                    "time_sec": round(t_sec, 6),
                    "player_id": int(player_id),
                    "team": assign.get(player_id, -1),
                    "tactical_px_x": tx,
                    "tactical_px_y": ty,
                    "tactical_m_x": mx,
                    "tactical_m_y": my,
                    "distance_step_m": dists.get(player_id),
                    "speed_kmh": speeds.get(player_id),
                }
            )

    df_players = pd.DataFrame(player_rows)
    df_players.to_csv(os.path.join(export_dir, "players_long.csv"), index=False)
