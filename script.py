from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import time

# Dar a Selenium la pagina de inicio de Instragram y navegar a ella
#Ubicacion del driver de Chrome
file_path = 'C:/python_webdriver/chromedriver.exe'
#Inicializar el driver de Chrome (El explorador Chrome debe estar instalado en el equipo)
driver = webdriver.Chrome(file_path)
#Le decimos la URL a que queremos ir
driver.get("http://www.instagram.com")

def ingresar_instagram(usuario, contra):
    #Obtenemos los elementos donde la página espera recibir el usuario y la contraseña
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    #Enviamos el usuario y contraseña de nuestra cuenta de Instragram para poder ingresar
    username.clear()
    password.clear()
    username.send_keys(usuario)
    password.send_keys(contra)

    #Hacemos click en el boton [Iniciar sesión]
    Login_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

    #Hacemos click en el primer texto de [Ahora no]
    not_now = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ahora no')]"))).click()

    #Hacemos click en el segundo texto de [Ahora no]
    not_now2 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ahora no')]"))).click()

def buscar_usuario(usuario):
    ##Ubicamos el objeto de la caja de búsqueda
    searchbox = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Buscar']")))
    searchbox.clear()

    #Definimos y enviamos el keyword (usuario) que queremos buscar y esperamos dos segundos
    keyword = usuario
    searchbox.send_keys(keyword)
    time.sleep(2)

    #Presionamos la tecla Enter dos veces esperando dos segundos despues de cada uno
    searchbox.send_keys(Keys.ENTER)
    time.sleep(2)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(2)

def obtener_link_post(driver):
    ##Leer post
    images = driver.find_elements_by_tag_name('a')
    images = [image.get_attribute('href') for image in images]
    matching = [s for s in images if "https://www.instagram.com/p/" in s] #todos los post tienen esta forma

    return matching

def obtener_lista_post():
    # Obtenemos la altura inicial del scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    #print('initial ',last_height)

    # Aca guardaremos los links. Inicializamos con los primeros que vemos al ingresar al perfil
    acum = obtener_link_post(driver)
    while True:
        # Hacemos scroll hasta abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Esperamos a que cargue la pagina
        time.sleep(3)

        # Agregamos los links a los que tenemos acceso en este momento. Puede incluir repetidos
        acum.extend(obtener_link_post(driver))
        #print('acumulados ',len(acum))    

        # Calculamos la nueva altura para scroll y comprobamos con la anterior para saber si ya llegamos al final
        new_height = driver.execute_script("return document.body.scrollHeight")
        #print('new ',last_height)

        # Validamos si ya llegamos hasta el final
        if new_height == last_height:
            break
        last_height = new_height

    # Como tenemos duplicados al crear un diccionario volvemos unicos los registros
    posts_links = list(dict.fromkeys(acum))
    print ("Cantidad de links de Posts: ", len(posts_links))

    #Guardar DataFrame con los datos
    df = pd.DataFrame(posts_links)
    df.to_csv('links_post.csv', index=False, encoding='utf-8')

def validar_xpath(xpath):
    # Verificar si hay elementos
    try:
        driver.find_element_by_xpath(xpath)
    except:
        return False
    return True

def obtener_info_post(listaLinksPost):
    # Post
    listaLinkPostP = []
    listaComentarios = []
    listaLikes = []
    listaDates = []
    listaNumPost = []
    # Video
    listaLinkPostV = []
    listaComentariosVideo = []
    listaPlayBacks = []
    listaDatesVideo = []
    listaNumPostVideo = []

    cont = 0
    cont1 = 0 
    conttime = 1
    for elemento in listaLinksPost:
        print(conttime)

        # Abrir post
        driver.get(elemento)

        # Cargar todos los comentarios
        while validar_xpath("//div/ul/li/div/button"):
            load_more_comments_element = driver.find_element_by_xpath("//div/ul/li/div/button")
            load_more_comments_element.click()
            time.sleep(1)

        time.sleep(2)

        # Contenido general de la pagina
        soup = BeautifulSoup(driver.page_source,'lxml')

        # Validacion
        validate_video = soup.find('div',attrs={'class':'Btbrr'})
        soup_8 = BeautifulSoup(str(validate_video),'lxml')                            
        validate_label_video = soup_8.find('video')

        validate_like = soup.find('div',attrs={'class':'Nm9Fw'})
        soup_9 = BeautifulSoup(str(validate_like),'lxml')                            
        validate_label_span = soup_9.find('span')

        # Si la pagina se queda en blanco, recargarla nuevamente
        if validate_label_span==None and validate_label_video==None:
            driver.get(elemento)

            soup = BeautifulSoup(driver.page_source,'lxml')

            # Validacion
            validate_video = soup.find('div',attrs={'class':'_5wCQW'})
            soup_8 = BeautifulSoup(str(validate_video),'lxml')                            
            validate_label_video = soup_8.find('video')

            validate_like = soup.find('div',attrs={'class':'Nm9Fw'})
            soup_9 = BeautifulSoup(str(validate_like),'lxml')                            
            validate_label_span = soup_9.find('span')

        # POST
        if validate_label_video == None or validate_label_span != None:
            # Traer los comentarios del post
            comms = soup.find_all('div',attrs={'class':'C4VMK'})
            soup_2 = BeautifulSoup(str(comms),'lxml')                            
            label_spans = soup_2.find_all('span')
            listaComentarios.append([i.text.strip() for i in label_spans if i != ''])
            listaNumPost.append([cont for i in range(len(label_spans)) if  i%2 == 1])

            # Traer los likes del post
            like = soup.find('div',attrs={'class':'Nm9Fw'})
            soup_3 = BeautifulSoup(str(like),'lxml')                            
            label_span = soup_3.find('span')
            listaLikes.append([label_span.text.strip()])

            # Traer la fecha del post
            date = soup.find('time',attrs={'class':'_1o9PC Nzb55'})
            soup_4 = BeautifulSoup(str(date),'lxml')
            listaDates.append([soup_4.text.strip()])

            # Traer link de post
            listaLinkPostP.append(elemento)

            cont += 1   
        # VIDEO  
        else:
            # Traer los comentarios del video
            comms_video = soup.find_all('div',attrs={'class':'C4VMK'})
            soup_5 = BeautifulSoup(str(comms_video),'lxml')                            
            label_spans_video = soup_5.find_all('span')
            listaComentariosVideo.append([i.text.strip() for i in label_spans_video if i != ''])
            listaNumPostVideo.append([cont1 for i in range(len(label_spans_video)) if  i%2 == 1])

            # Traer las reproducciones del video
            playbacks = soup.find('div',attrs={'class':'HbPOm _9Ytll'})
            soup_5 = BeautifulSoup(str(playbacks),'lxml')                            
            label_span_video = soup_5.find('span')
            listaPlayBacks.append([label_span_video.text.strip()])

            # Traer la fecha del post
            date_video = soup.find('time',attrs={'class':'_1o9PC Nzb55'})
            soup_7 = BeautifulSoup(str(date_video),'lxml')
            listaDatesVideo.append([soup_7.text.strip()])

            # Traer link de post video
            listaLinkPostV.append(elemento)

            cont1 += 1        
                    
        conttime += 1
        time.sleep(3)

    return listaLinkPostP, listaComentarios, listaLikes, listaDates, listaNumPost, listaLinkPostV, listaComentariosVideo, listaPlayBacks, listaDatesVideo, listaNumPostVideo

def transformar_listas(listaLinksPost, listaComentarios, listaLikes, listaDates, listaNumPost):
    listaModComentarios = []
    listaUsuarios = []
    listaModLikes = []
    listaModDates = []
    listaAuxModDates = []
    listaModLinkPost = []
    listaLinkDateUserComens = []
    listaLinkDateLikes = []
    fecha = ''
    anio = ''

    # Des-agrupar la lista de likes
    for i in range(len(listaLikes)):
        for j in range(len(listaLikes[i])):
            listaModLikes.append(listaLikes[i][j])

    # Transformar fecha y asignar el año en curso
    for i in range(len(listaDates)):
        for j in range(len(listaDates[i])):
            fecha = listaDates[i][j]
            fecha = fecha.replace('de','/')
            fecha = fecha.replace(' ','')
            anio = fecha[int(len(fecha)-4):]
            if anio!='2020' and anio!='2019' and anio!='2018' and anio!='2017' and anio!='2015' and anio!='2014' and anio!='2013' and anio!='2012':
                fecha = fecha + '/2021'
            listaAuxModDates.append(fecha)

    # Des-agrupar y descombinar las listas, para tener la de comentarios y usuarios
    for i in range(len(listaComentarios)):
        for j in range(len(listaComentarios[i])):
            if j%2==1:
                listaModComentarios.append(listaComentarios[i][j])
            else:
                listaUsuarios.append(listaComentarios[i][j])

    # Duplicar links y fechas con la cantidad de comentarios
    for i in range(len(listaNumPost)):
        for j in range(len(listaNumPost[i])):
            listaModDates.append(listaAuxModDates[listaNumPost[i][j]])
            listaModLinkPost.append(listaLinksPost[listaNumPost[i][j]])

    # Concatenar arrays links, fechas, usuarios, comentarios
    listaLinkDateUserComens = list(zip(listaModLinkPost,listaModDates,listaUsuarios,listaModComentarios))

    # Concatenar links, fechas y likes
    listaLinkDateLikes = list(zip(listaLinksPost,listaAuxModDates,listaModLikes))

    return listaLinkDateUserComens, listaLinkDateLikes

def main():
    listaLinksPost = []
    # Post
    listaLinkPostP = []
    listaComentarios = []
    listaLikes = []
    listaDates = []
    listaNumPost = []
    # Post video
    listaComentariosVideo = []
    listaDatesVideo = []
    listaNumPostVideo = []
    listaPlayBacks = []
    listaLinkPostV = []
    # Finales
    listaLinkDateUserComensP = []
    listaLinkDateLikesP = []
    listaLinkDateUserComensV = []
    listaLinkDateLikesV = []
    #
    listaLinksPost = []
    resp = 0

    ingresar_instagram('usuario', 'contraseña')
    buscar_usuario('red.papaz')

    print('--------MENU--------\n1. Links de los post \n2. Obtener data de los post')
    resp = int(input('Ingrese la operación a realizar: '))

    if resp == 1:
        obtener_lista_post()
        driver.quit()
    elif resp == 2:
        # Leer archivo csv
        dfCsv = pd.read_csv("12.csv")
        listaAux = dfCsv.values.tolist()

        # Ya que retorna una lista de listas, la convertimos a una sola
        for i in range(len(listaAux)):
            for j in range(len(listaAux[i])):
                listaLinksPost.append(listaAux[i][j])

        listaLinkPostP, listaComentarios, listaLikes, listaDates, listaNumPost, listaLinkPostV, listaComentariosVideo, listaPlayBacks, listaDatesVideo, listaNumPostVideo = obtener_info_post(listaLinksPost)

        listaLinkDateUserComensP, listaLinkDateLikesP = transformar_listas(listaLinkPostP, listaComentarios, listaLikes, listaDates, listaNumPost)
        listaLinkDateUserComensV, listaLinkDateLikesV = transformar_listas(listaLinkPostV, listaComentariosVideo, listaPlayBacks, listaDatesVideo, listaNumPostVideo)

        # Dataframes y exportar excel

        df = pd.DataFrame(listaLinkDateUserComensP,columns=['LINK POST','FECHA','USUARIO','COMENTARIO'])
        df.to_excel('data_comentarios_post.xlsx')  

        df1 = pd.DataFrame(listaLinkDateLikesP,columns=['LINK POST','FECHA','LIKES'])
        df1.to_excel('data_likes_post.xlsx')  

        df2 = pd.DataFrame(listaLinkDateUserComensV,columns=['LINK POST','FECHA','USUARIO','COMENTARIO'])
        df2.to_excel('data_comentarios_video.xlsx')  

        df3 = pd.DataFrame(listaLinkDateLikesV,columns=['LINK POST','FECHA','REPRODUCCIONES'])
        df3.to_excel('data_likes_video.xlsx')  

        driver.quit()

if __name__ == '__main__':
    main()
