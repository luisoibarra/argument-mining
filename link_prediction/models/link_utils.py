


def create_lr_annealing_function(initial_lr=0.001, k=0.001, fixed_epoch=-1):

    def lr_annealing(epoch, lr=0):
        """
        # Arguments
            epoch (int): The number of epochs
        # Returns
            lr (float32): learning rate
        """
        if fixed_epoch <= 0:
            lr = (initial_lr / (1 + k * epoch))
        else:
            lr = (initial_lr / (1 + k * fixed_epoch))
        print("\tNEW LR: " + str(lr))

        return lr

    return lr_annealing

