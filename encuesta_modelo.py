import telebot
from telebot import types
import pymongo
import sys
import joblib
import os
from dotenv import load_dotenv

load_dotenv()
URI = os.getenv('URI')
TOKEN = os.getenv('TOKEN')

# db

client = pymongo.MongoClient(URI)

db = client["hackatecnm"]
collection = db["filtro"]

# bot

bot = telebot.TeleBot(TOKEN)

respuestas = {}

preguntas_respuestas = [
  {
    "pregunta": "¿Cuál es tu sexo?",
    "respuestas": ["Masculino", "Femenino"]
  },
  {
    "pregunta": "¿Eres fumador?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes dedos amarillos?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Sufres de ansiedad?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes presión de grupo?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes alguna enfermedad crónica?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Sufres de fatiga?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes alguna alergia?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes sibilancias?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Consumes alcohol constantemente?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Sufres de tos?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes dificultad para respirar?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes dificultad para tragar?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Tienes dolor de pecho?",
    "respuestas": ["Sí", "No"]
  },
  {
    "pregunta": "¿Cuántos años tienes?",
    "respuestas": []
  }
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, 'Bienvenid@ a la encuesta para medir la evaluación de riesgo de Cáncer de pulmón.')
  bot.reply_to(message, 'Escribe o da clic en /preguntas para comenzar. (:')


@bot.message_handler(commands=['help'])
def send_help(message):
  bot.reply_to(message, 'En caso de haber respondido algo mal algo, escribe /preguntas.')


indice = 0

@bot.message_handler(commands=['preguntas'])
def handle_start(message):
  send_question(message)

@bot.message_handler(func=lambda message: True)
def handle_answers(message):
  global indice
  respuesta = message.text
  if respuesta in preguntas_respuestas[indice]["respuestas"] or (preguntas_respuestas[indice]["pregunta"] == "¿Cuántos años tienes?"):
    if respuesta == "Sí":
      respuestas[indice + 1] = 2
    elif respuesta == "No":
      respuestas[indice + 1] = 1
    elif respuesta == "Masculino":
      respuestas[indice + 1] = 1
    elif respuesta == "Femenino":
      respuestas[indice + 1] = 0
    else:
      respuestas[indice + 1] = int(respuesta)
    indice += 1
    if indice < len(preguntas_respuestas):
      send_question(message)
    else:
      bot.reply_to(message, "¡Gracias por participar!")
      final_respuestas = {str(key): value for key, value in respuestas.items()}
      collection.insert_one(final_respuestas)
      bot.reply_to(message, "Cargando la predicción...")
      print(respuestas.values())
      modelo = joblib.load('best_model_tree.joblib')
      prediccion = modelo.predict(respuestas.values())
      bot.reply_to(message, "El resultado de la predcción es: ", prediccion)

  else:
    bot.reply_to(message, "Por favor elige una de las opciones proporcionadas.")

def send_question(message):
  pregunta = preguntas_respuestas[indice]["pregunta"]
  respuestas_posibles = preguntas_respuestas[indice]["respuestas"]
  markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
  for respuesta in respuestas_posibles:
    markup.add(respuesta)
  bot.send_message(message.chat.id, pregunta, reply_markup=markup)


if __name__ == '__main__':
  bot.polling(non_stop=True)
  client.close()
  sys.exit()
