#!/usr/bin/env python3
import time

import torch.multiprocessing as mp

from common import experience


def play_func(exp_queue):
    frame_idx = 0

    while True:
        frame_idx += 1
        exp = frame_idx
        exp_queue.put(exp)

        print(frame_idx)

        if frame_idx >= 1000:
            break

    exp_queue.put(None)


def main():
    mp.set_start_method('spawn')

    buffer = experience.ExperienceReplayBuffer(experience_source=None, buffer_size=100000)

    train_freq = 4
    batch_size = 32
    replay_initial = 100

    exp_queue = mp.Queue(maxsize=train_freq * 2)
    play_proc = mp.Process(target=play_func, args=(exp_queue,))
    play_proc.start()

    while play_proc.is_alive():
        for _ in range(train_freq):
            exp = exp_queue.get()
            if exp is None:
                play_proc.join()
                break
            buffer._add(exp)

        if len(buffer) < replay_initial:
            continue

        batch = buffer.sample(batch_size)
        print(batch, " - ", len(batch))
        time.sleep(1)


if __name__ == "__main__":
    main()