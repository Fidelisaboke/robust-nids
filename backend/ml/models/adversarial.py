import tensorflow as tf

# Define the loss object
bce = tf.keras.losses.BinaryCrossentropy()


@tf.function
def generate_fgsm_samples(model, X_malicious, y_target, epsilon=0.1):
    """
    Generates adversarial samples using FGSM.
    X_malicious must be a Tensor.
    """
    X_malicious_tf = tf.cast(X_malicious, dtype=tf.float32)
    y_target_tf = tf.cast(y_target, dtype=tf.float32)

    with tf.GradientTape() as tape:
        tape.watch(X_malicious_tf)
        prediction = model(X_malicious_tf, training=False)
        loss = bce(y_target_tf, prediction)

    gradient = tape.gradient(loss, X_malicious_tf)
    signed_grad = tf.sign(gradient)

    # Evasion attack: move "downhill" towards the benign (0) class
    adv_sample = X_malicious_tf - epsilon * signed_grad

    # Clip values to [0, 1] range (since data was MinMaxScaler'd)
    adv_sample = tf.clip_by_value(adv_sample, 0, 1)

    return adv_sample
