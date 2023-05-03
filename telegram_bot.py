#https://api.telegram.org/bot6147927066:AAHGd7ogh5qknKlVjSgROOm-_Z_JHT93xQA/getUpdates


import logging
import math
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


token = "6147927066:AAHGd7ogh5qknKlVjSgROOm-_Z_JHT93xQA"
chat_group_id = "-1001829782835" #Cajonera. Es el numero que aparece en la URL cuando se entra por web

distancia_para_toma_wp = 10 #km
wp_cercanos=[ {'location': {'latitude':-34.91511667,'longitude':-56.12248333},'description': 'Boya Coquimbo'}, #Cerca Coquimbo
              {'location': {'latitude':-34.93321667,'longitude':-56.11543333},'description': 'Cercanias de la Ciega'}, #Cerca de la Ciega
              {'location': {'latitude':-34.93321667,'longitude':-56.11543333},'description': 'Cercanias de la Ciega'} #Cerca de la Ciega
]



## Variables internas
current_wp = 0
indices_cercanos = [0]*len(wp_cercanos)
for i in range(len(wp_cercanos)):
    indices_cercanos[i] = i
print(indices_cercanos)



def haversine(lat1, lon1, lat2, lon2):
   rad=math.pi/180
   dlat=lat2-lat1
   dlon=lon2-lon1
   R=6372.795477598
   a=(math.sin(rad*dlat/2))**2 + math.cos(rad*lat1)*math.cos(rad*lat2)*(math.sin(rad*dlon/2))**2
   distancia=2*R*math.asin(math.sqrt(a))
   return distancia

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_wp
    global current_wp_indice
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Mezclando Waypoints!")
    random.shuffle(indices_cercanos)
    logging.info(indices_cercanos)
    current_wp=0
    current_wp_indice=indices_cercanos[current_wp]
    wp=wp_cercanos[current_wp_indice]
    await context.bot.send_message(chat_id=chat_group_id, text="Waypoint a buscar: **{}**".format(wp['description']))
    await context.bot.send_location(chat_id=chat_group_id, latitude=wp['location']['latitude'],longitude=wp['location']['longitude']) 
   

async def wp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_wp
    global current_wp_indice    
    current_wp_indice=indices_cercanos[current_wp]
    wp=wp_cercanos[current_wp_indice]

    await context.bot.send_message(chat_id=chat_group_id, text="Waypoint a buscar: **{}**".format(wp['description']))
    await context.bot.send_location(chat_id=chat_group_id, latitude=wp['location']['latitude'],longitude=wp['location']['longitude'])

async def LocationMessageEvent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     global current_wp
     global current_wp_indice
     current_wp_indice=indices_cercanos[current_wp]
     wp=wp_cercanos[current_wp_indice]
     user = update.message.from_user
     user_location = update.message.location
     logging.info("Location of {}: ({}, {})".format(
                 user.first_name, user_location.latitude,
                 user_location.longitude))
     # Longitud: 113.37935836 Latitud: 31.71785761
     # La longitud este es la longitud positiva, la longitud oeste es la longitud negativa, la latitud norte es la latitud 90, la latitud sur es 90 + latitud
     # Los datos anteriores son longitud este y latitud norte
     Mlng_A = user_location.longitude
     Mlat_A = user_location.latitude


     Mlng_B = wp['location']['longitude']
     Mlat_B = wp['location']['latitude']
     Distance = round(haversine(Mlat_A, Mlng_A, Mlat_B, Mlng_B))
     logging.info("Distancia al WP of {}: {} km".format(
                 user.first_name, Distance))
     if Distance > distancia_para_toma_wp :                 
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Estas a {} km".format(Distance))
     else :    
        await context.bot.send_message(chat_id=update.effective_chat.id, text="LLegaste")
        await context.bot.send_message(chat_id=chat_group_id, text="{} LLego!!".format(user.first_name))
        current_wp=current_wp+1
        if current_wp == len(wp_cercanos) :
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Termino el juego!!")
        else:    
            current_wp_indice=indices_cercanos[current_wp]
            wp=wp_cercanos[current_wp_indice]
            await context.bot.send_message(chat_id=chat_group_id, text="Waypoint a buscar: **{}**".format(wp['description']))
            await context.bot.send_location(chat_id=chat_group_id, latitude=wp['location']['latitude'],longitude=wp['location']['longitude']) 
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    wp_handler = CommandHandler('wp', wp)
    application.add_handler(wp_handler)
    
    loc_handler= MessageHandler(filters.LOCATION , LocationMessageEvent)
    application.add_handler(loc_handler)
    
    application.run_polling()