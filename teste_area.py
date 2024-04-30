# %%
import tensorflow as tf
import numpy as np

# Defina os dados de treinamento
inputs = ['Qual é o seu nome?', 'Como posso te chamar?', 'Por favor, diga-me seu nome.']
outputs = ['Meu nome é ', 'Você pode me chamar de ', 'Chame-me de ']

# Tokenize os dados de entrada e saída
tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='')
tokenizer.fit_on_texts(inputs + outputs)
vocab_size = len(tokenizer.word_index) + 1

# Converta as sequências de texto em sequências de números
inputs_sequences = tokenizer.texts_to_sequences(inputs)
outputs_sequences = tokenizer.texts_to_sequences(outputs)

# Pad os sequências para terem o mesmo comprimento
max_length = max(len(seq) for seq in inputs_sequences + outputs_sequences)
inputs_sequences = tf.keras.preprocessing.sequence.pad_sequences(inputs_sequences, maxlen=max_length, padding='post')
outputs_sequences = tf.keras.preprocessing.sequence.pad_sequences(outputs_sequences, maxlen=max_length, padding='post')

# Crie o modelo de chatbot
embedding_dim = 256
units = 1024

# Codificador
encoder_inputs = tf.keras.layers.Input(shape=(None,))
encoder_embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim, mask_zero=True)(encoder_inputs)
encoder_lstm = tf.keras.layers.LSTM(units, return_state=True)
encoder_outputs, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

# Decodificador
decoder_inputs = tf.keras.layers.Input(shape=(None,))
decoder_embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim, mask_zero=True)(decoder_inputs)
decoder_lstm = tf.keras.layers.LSTM(units, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = tf.keras.layers.Dense(vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Modelo final
model = tf.keras.models.Model([encoder_inputs, decoder_inputs], decoder_outputs)

# Compile o modelo
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Treine o modelo
model.fit([inputs_sequences, outputs_sequences[:, :-1]], outputs_sequences[:, 1:], batch_size=64, epochs=50)

# Função para conversar com o chatbot
def chat():
    while True:
        # Obter a entrada do usuário
        user_input = input("Você: ")
        
        # Converter a entrada do usuário em sequência de números
        input_seq = tokenizer.texts_to_sequences([user_input])
        input_seq = tf.keras.preprocessing.sequence.pad_sequences(input_seq, maxlen=max_length, padding='post')
        
        # Obter a resposta do modelo
        predicted_output = model.predict([input_seq, np.zeros((1, max_length))])
        
        # Converter a saída predita em texto
        predicted_output = np.argmax(predicted_output, axis=-1)
        predicted_output = [tokenizer.index_word[idx] for idx in predicted_output[0] if idx != 0]
        response = ' '.join(predicted_output)
        
        # Exibir a resposta do chatbot
        print("Chatbot:", response)

# Iniciar a conversa com o chatbot
chat()