import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from tensorflow.keras.utils import Sequence, to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, MaxPooling3D, TimeDistributed, Flatten, LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
# --- Configuration ---
PROCESSED_DATA_DIR = "processed_data/"
OUTPUT_DIR = "model/"
MODEL_SAVE_PATH = os.path.join(OUTPUT_DIR, "lip_reader_cnn_lstm.h5")
BATCH_SIZE = 1 # Set to 1 for very small datasets
EPOCHS = 50
LEARNING_RATE = 0.0001
INPUT_SHAPE = (22, 80, 112, 1) # Frames, Height, Width, Channels

class DataGenerator(Sequence):
    def __init__(self, file_paths, labels, batch_size, num_classes, shuffle=True):
        self.file_paths = file_paths
        self.labels = labels
        self.batch_size = batch_size
        self.num_classes = num_classes
        self.shuffle = shuffle
        self.indexes = np.arange(len(self.file_paths))
        self.on_epoch_end()

    def __len__(self): # Corrected from _len_
        return int(np.floor(len(self.file_paths) / self.batch_size))

    def __getitem__(self, index): # Corrected from _getitem_
        batch_indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]
        batch_paths = [self.file_paths[i] for i in batch_indexes]
        batch_labels = [self.labels[i] for i in batch_indexes]
        
        X = np.array([np.load(file_path) for file_path in batch_paths])
        X = np.expand_dims(X, axis=-1)
        y = to_categorical(batch_labels, num_classes=self.num_classes)
        
        return X, y

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)

# --- Model Architecture (Unchanged) ---
def build_cnn_lstm_model(num_classes):
    model = Sequential([
        Conv3D(16, (3, 5, 5), activation='relu', input_shape=INPUT_SHAPE, padding='same'),
        MaxPooling3D((1, 2, 2)),
        BatchNormalization(),
        
        Conv3D(32, (3, 3, 3), activation='relu', padding='same'),
        MaxPooling3D((1, 2, 2)),
        BatchNormalization(),
        
        Conv3D(64, (3, 3, 3), activation='relu', padding='same'),
        MaxPooling3D((1, 2, 2)),
        BatchNormalization(),

        TimeDistributed(Flatten()),
        
        LSTM(128, return_sequences=False),
        Dropout(0.5),
        
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    return model

# --- NEW FUNCTION: Plot Training History ---
def plot_training_history(history, output_dir):
    """Plots and saves the training and validation accuracy and loss."""
    # Plot accuracy
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    # Plot loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_history.png'))
    plt.show()
    print(f"✅ Training history plots saved to {output_dir}")

# --- UPDATED FUNCTION: Plot Confusion Matrix ---
def plot_confusion_matrix(model, generator, class_names, output_dir):
    """Calculates, plots, and saves the confusion matrix."""
    # Predict probabilities for the entire validation set
    y_pred_probs = model.predict(generator)
    # Get the class with the highest probability for each prediction
    y_pred = np.argmax(y_pred_probs, axis=1)
    # Get the true labels from the generator
    y_true = generator.labels
    
    # Ensure y_true has the same length as y_pred
    # This handles cases where the last batch is not full
    if len(y_true) != len(y_pred):
        num_batches = len(generator)
        y_true = y_true[:num_batches * generator.batch_size]
        y_true = y_true[:len(y_pred)]

    # ✨ FIX: Get the unique labels that are ACTUALLY in the validation set
    unique_labels = np.unique(np.concatenate((y_true, y_pred)))
    
    # ✨ FIX: Filter the class names to only include those present in the validation set
    actual_class_names = [class_names[i] for i in unique_labels]

    # Calculate the confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=unique_labels)
    
    # Plot the confusion matrix using the corrected labels
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=actual_class_names)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    disp.plot(ax=ax, cmap='Blues', xticks_rotation='vertical')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.show()
    print(f"✅ Confusion matrix saved to {output_dir}")

# --- Main Training Script ---
if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load file paths and labels
    words = sorted([
        d for d in os.listdir(PROCESSED_DATA_DIR) 
        if os.path.isdir(os.path.join(PROCESSED_DATA_DIR, d)) and d != 'metadata'
    ])
    if not words:
        print(f"Error: No processed data found in '{PROCESSED_DATA_DIR}'.")
        exit()

    word_to_index = {word: i for i, word in enumerate(words)}
    NUM_CLASSES = len(words)
    print(f"Training on {NUM_CLASSES} words: {words}")

    X_paths, y_labels = [], []
    for word, index in word_to_index.items():
        word_dir = os.path.join(PROCESSED_DATA_DIR, word)
        for take_file in os.listdir(word_dir):
            if take_file.endswith(".npy"):
                file_path = os.path.join(word_dir, take_file)
                X_paths.append(file_path)
                y_labels.append(index)
    # Debug: print found files per class
    print("\nFound .npy files:")
    for word, index in word_to_index.items():
        word_dir = os.path.join(PROCESSED_DATA_DIR, word)
        npy_files = [f for f in os.listdir(word_dir) if f.endswith('.npy')]
        print(f"  {word}: {len(npy_files)} files -> {npy_files}")
    print(f"Total samples: {len(X_paths)}")
    if not X_paths:
        print("Error: No .npy files found.")
        exit()


    # Check if any class has only 1 sample
    from collections import Counter
    class_counts = Counter(y_labels)
    min_class_count = min(class_counts.values())
    if min_class_count < 2:
        print("\n⚠ Only 1 sample found in at least one class. Skipping train/val split.")
        X_train_paths, X_val_paths = X_paths, X_paths
        y_train, y_val = y_labels, y_labels
    else:
        X_train_paths, X_val_paths, y_train, y_val = train_test_split(
            X_paths, y_labels, test_size=0.5, random_state=42, stratify=y_labels
        )
    print(f"\nTrain samples: {len(X_train_paths)}")
    print(f"Val samples: {len(X_val_paths)}")
    print(f"Train files: {X_train_paths}")
    print(f"Val files: {X_val_paths}")

    class_weights = class_weight.compute_class_weight(
        'balanced', classes=np.unique(y_train), y=y_train
    )
    class_weights_dict = dict(enumerate(class_weights))
    print("Class weights calculated:", class_weights_dict)

    # Create data generators
    train_generator = DataGenerator(X_train_paths, y_train, BATCH_SIZE, NUM_CLASSES)
    val_generator = DataGenerator(X_val_paths, y_val, BATCH_SIZE, NUM_CLASSES, shuffle=False)
    
    # Build and compile the model
    model = build_cnn_lstm_model(NUM_CLASSES)
    optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])
    model.summary()
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_accuracy', save_best_only=True, mode='max', verbose=1),
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1),
        # ✨ NEW: Reduce learning rate when validation loss plateaus
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.00001, verbose=1)
    ]

    # Train the model
    print("\nTraining model...")
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        callbacks=callbacks,
        class_weight=class_weights_dict
    )

    print(f"\n✅ Training complete. Best model saved to {MODEL_SAVE_PATH}")
    
    # Evaluate and visualize results
    print("\n--- Final Evaluation ---")
    loss, accuracy = model.evaluate(val_generator)
    print(f"Final Validation Accuracy: {accuracy:.4f}")
    
    # ✨ NEW: Call the new plotting functions
    plot_training_history(history, OUTPUT_DIR)
    plot_confusion_matrix(model, val_generator, class_names=words, output_dir=OUTPUT_DIR)