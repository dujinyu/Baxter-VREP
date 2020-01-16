import random
import sys
import pickle
import torch
import td3.constants as cons


def populate_buffer(sim, replay_buffer):
    print("\nInitializing experience replay buffer...")
    buffer_storage = []

    # store and load the initial replay values
    # once replay buffer is full, use the pre-made one to populate observe step
    replay_counter = 0

    with open("D:\\git\\PythonProjects\\Baxter-VREP\\td3\\temp\\buffer.pkl", "rb") as pk_file:
        while True:
            try:
                data = pickle.load(pk_file)
                for test in data:
                    replay_buffer.add(test[0], torch.tensor(test[1], dtype=torch.float32), test[2], test[3], test[4])
                    buffer_storage.append([test[0], test[1], test[2], test[3], test[4]])
                    replay_counter += 1
            except EOFError:
                print('Reached end of file.')
                break
            except pickle.UnpicklingError:
                print('Incomplete record {} was ignored.'.format(replay_counter + 1))
                break

    # save_buffer = open("D:\\git\\PythonProjects\\Baxter-VREP\\td3\\temp\\buffer.pkl", "wb")
    # pickle.dump(buffer_storage, save_buffer)
    # save_buffer.close()
    buffer_storage = []
    buffer = cons.BUFFER_SIZE - replay_counter
    print('Buffer size {}/{} loaded from previous session'.format(replay_counter, cons.BUFFER_SIZE))

    distance = 0
    for x in range(buffer):

        state = sim.get_input_image()

        value = [-0.1, 0, 0.1]
        action = []
        for i in range(7):
            action.append(random.choice(value))

        sim.step_right(action)
        next_state = sim.get_input_image()
        new_distance = sim.calc_distance()
        if new_distance > distance:
            reward = -1
        elif new_distance == distance:
            reward = 0
        else:
            reward = 1
        right_arm_collision_state = sim.get_collision_state()

        if new_distance < cons.SOLVED_DISTANCE:
            done = True
        elif right_arm_collision_state:
            done = True
        else:
            done = False

        distance = new_distance
        replay_buffer.add(state, torch.tensor(action, dtype=torch.float32), reward, next_state, done)

        # TODO save the observations, for testing , remove later after testing
        buffer_storage.append([state, action, reward, next_state, done])

        if done:
            sim.reset_sim()

        if x % 25 == 0:
            save_buffer = open("D:\\git\\PythonProjects\\Baxter-VREP\\td3\\temp\\buffer.pkl", "ab")
            pickle.dump(buffer_storage, save_buffer)
            save_buffer.close()
            buffer_storage = []
            sim.reset_sim()  # reset simulation after 25 movements
        # TODO this adds extra at the end... ie last group has 16, it adds 100, fix to make correct at end
        if x % 100 == 0:
            replay_counter += 100
            print("{} of {} loaded".format(replay_counter, cons.BUFFER_SIZE))

    print("\nExperience replay buffer initialized.")

    sys.stdout.flush()