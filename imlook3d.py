import matplotlib.pyplot as plt
import matplotlib.cm as cm

# views volumetric images
# input should be 3D volume and optionally the index of the image to display

def multi_slice_viewer(Image3D, current_idx = 0):
    remove_keymap_conflicts({'right', 'left'})
    fig, ax = plt.subplots()
    ax.volume = Image3D
    # store current image index
    ax.index = current_idx
    ax.imshow(Image3D[ax.index, :, :], cmap=cm.gray)
    ax.set_title('Current frame = {}'.format(ax.index))
    # use mpl_connect to connect process_key to figure
    fig.canvas.mpl_connect('key_press_event', process_key)


def process_key(event):
    fig = event.canvas.figure
    ax = fig.axes[0]
    if event.key == 'left':
        previous_slice(ax)
    elif event.key == 'right':
        next_slice(ax)
    fig.canvas.draw()

def previous_slice(ax):
    # go to previous slice
    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])
    # update figure title with correct frame
    ax.set_title('Current frame = {}'.format(ax.index))

def next_slice(ax):
    # go to next image
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[0]
    ax.images[0].set_array(volume[ax.index])
    # update figure title with correct frame
    ax.set_title('Current frame = {}'.format(ax.index))

def remove_keymap_conflicts(new_keys_set):
    for prop in plt.rcParams:
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)

