import telebot
import requests
import random
import time
from datetime import datetime, timedelta
from telebot import types

TOKEN = "7645024099:AAEZNIFe-vg0vDy6_RuE2oM5db5VjdE779k"
ADMIN_ID = 6908816326

bot = telebot.TeleBot(TOKEN)

user_signals = {}
premium_users = {}
last_signal_time = {}

def get_last_15_results():
    url = "https://crash-gateway-cc-cr.gamedev-tech.cc/history"
    params = {"id_n": "1play_luckyjet", "id_i": "1"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = [float(game['top_coefficient']) for game in data[:15]]
            return results
        else:
            return []
    except:
        return []

def analyse_tendance(results):
    moyenne = sum(results) / len(results)
    tendance = "📉 Basse" if moyenne < 2.5 else "📈 Haute"
    return moyenne, tendance

def faire_prediction():
    results = get_last_15_results()
    if not results:
        return "Impossible de récupérer les données."

    moyenne, tendance = analyse_tendance(results)
    dernier_resultat = results[0]

    if moyenne < 2.5:
        cote = round(random.uniform(2.0, 3.2), 2)
        assurance = round(random.uniform(1.5, 2.0), 2)
    else:
        cote = round(random.uniform(3.5, 5.5), 2)
        assurance = round(random.uniform(2.0, 2.8), 2)

    heure = (datetime.now() + timedelta(minutes=2)).strftime("%H:%M")

    message = (
        f"🎲 SIGNAL 🚀\n"
        f"╔══════════════════╗\n"
        f"◆ Cote : {cote}X\n"
        f"◆ Heure : {heure}\n"
        f"◆ Assurance : {assurance}X\n"
        f"◆ Dernier tour : {dernier_resultat}X\n"
        f"◆ Tendance : {tendance}\n"
        f"╚══════════════════╝"
    )
    return message

def faire_prediction_premium():
    results = get_last_15_results()
    if not results:
        return "Impossible de récupérer les données."

    moyenne, tendance = analyse_tendance(results)
    dernier_resultat = results[0]

    if moyenne < 2.5:
        cote = round(random.uniform(3.0, 4.5), 2)
        assurance = round(random.uniform(2.0, 2.5), 2)
    else:
        cote = round(random.uniform(4.5, 6.5), 2)
        assurance = round(random.uniform(2.5, 3.5), 2)

    heure = (datetime.now() + timedelta(minutes=2)).strftime("%H:%M")

    message = (
        f"⭐️ SIGNAL PREMIUM 🚀\n"
        f"╔══════════════════╗\n"
        f"◆ Cote : {cote}X\n"
        f"◆ Heure : {heure}\n"
        f"◆ Assurance : {assurance}X\n"
        f"◆ Dernier tour : {dernier_resultat}X\n"
        f"◆ Tendance : {tendance}\n"
        f"╚══════════════════╝"
    )
    return message

def menu_principal():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎲 SIGNAL", "⭐ PREMIUM")
    markup.add("📊 STATS", "🆓 GAGNER DES SIGNAUX")
    markup.add("👤 MON COMPTE")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in user_signals:
        user_signals[user_id] = 5
    bot.send_message(user_id, f"👋 Bienvenue {message.from_user.first_name} sur Lucky Jet Bot !", reply_markup=menu_principal())

@bot.message_handler(commands=['ajouter'])
def ajouter_signal(message):
    if message.from_user.id == ADMIN_ID:
        try:
            parts = message.text.split()
            if len(parts) != 3:
                bot.send_message(ADMIN_ID, "❌ Utilisation : /ajouter ID NOMBRE")
                return

            _, user_id, qty = parts
            user_id = int(user_id)
            qty = int(qty)

            user_signals[user_id] = user_signals.get(user_id, 0) + qty
            bot.send_message(ADMIN_ID, f"✅ {qty} signaux ajoutés à l'utilisateur {user_id}.")
        except ValueError:
            bot.send_message(ADMIN_ID, "❌ L'ID et le nombre doivent être des nombres entiers.")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Erreur : {e}")

@bot.message_handler(commands=['ajouterP'])
def ajouter_premium(message):
    if message.from_user.id == ADMIN_ID:
        try:
            parts = message.text.split()
            if len(parts) != 2:
                bot.send_message(ADMIN_ID, "❌ Utilisation : /ajouterP ID")
                return

            _, user_id = parts
            premium_users[int(user_id)] = True
            bot.send_message(ADMIN_ID, f"✅ Premium activé pour {user_id}.")
        except:
            bot.send_message(ADMIN_ID, "❌ Erreur, vérifie l'ID.")

@bot.message_handler(func=lambda m: m.text == "👤 MON COMPTE")
def mon_compte(message):
    user_id = message.from_user.id
    nom = message.from_user.first_name
    username = message.from_user.username or "Aucun"
    premium = "✅ Oui" if premium_users.get(user_id) else "❌ Non"
    signaux = user_signals.get(user_id, 0)

    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            bot.send_photo(user_id, file_id)
    except:
        pass

    bot.send_message(user_id, f"""
👤 *MON COMPTE*

*Nom* : {nom}
*Username* : @{username}
*ID* : `{user_id}`
*Premium* : {premium}
*Signaux restants* : {signaux}
""", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎲 SIGNAL")
def signal(message):
    user_id = message.from_user.id
    now = time.time()

    if user_signals.get(user_id, 0) == 0 and not premium_users.get(user_id):
        bot.send_message(user_id, "❌ Vous n'avez plus de signaux disponibles.")
        return

    if now - last_signal_time.get(user_id, 0) < 180:
        bot.send_message(user_id, "⏳ Patientez 3 minutes entre chaque signal.")
        return

    prediction = faire_prediction()
    bot.send_message(user_id, prediction)

    if not premium_users.get(user_id):
        user_signals[user_id] -= 1

    last_signal_time[user_id] = now

@bot.message_handler(func=lambda m: m.text == "⭐ PREMIUM")
def signal_premium(message):
    user_id = message.from_user.id
    now = time.time()

    if not premium_users.get(user_id):
        bot.send_message(user_id, "❌ Cette option est réservée aux utilisateurs Premium.")
        return

    if now - last_signal_time.get(user_id, 0) < 180:
        bot.send_message(user_id, "⏳ Patientez 3 minutes entre chaque signal.")
        return

    prediction = faire_prediction_premium()
    bot.send_message(user_id, prediction)

    last_signal_time[user_id] = now

@bot.message_handler(func=lambda m: m.text == "📊 STATS")
def stats(message):
    results = get_last_15_results()
    if results:
        moyenne, tendance = analyse_tendance(results)
        bot.send_message(message.chat.id, f"📊 Moyenne : {round(moyenne, 2)}X\n📈 Tendance : {tendance}")
    else:
        bot.send_message(message.chat.id, "Impossible de récupérer les stats.")

@bot.message_handler(func=lambda m: m.text == "🆓 GAGNER DES SIGNAUX")
def gagner(message):
    bot.send_message(message.chat.id, "Partage le bot à tes amis pour gagner des signaux supplémentaires !")

bot.polling()