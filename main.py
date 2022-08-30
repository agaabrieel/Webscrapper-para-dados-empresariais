import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def scraping():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

    links = []

    dados = {'CNPJ': [], 'Razão Social': [], 'Nome Fantasia': [], 'Tipo': [],
             'Situação Cadastral': [], 'Data de Abertura': [], 'Data da Situação Cadastral': [],
             'Capital Social': [], 'Natureza Jurídica': [], 'Empresa MEI': [],
             'Logradouro': [], 'Número': [], 'Complemento': [], 'CEP': [],
             'Bairro': [], 'Município': [], 'UF': [], 'Telefone': [],
             'E-MAIL': [], 'Quadro Societário': [], 'Atividade Principal': [],
             'Atividades Secundárias': [], 'Data da Consulta': []}

    print(os.getcwd())

    main_link = input('Entre o link: ')
 
    driver = webdriver.Chrome(os.getcwd() + '\chromedriver')

    driver.get(main_link)

    search_button = driver.find_element(
        By.XPATH, '//*[@id="__layout"]/div/div[2]/section/div[6]/div/div/button[1]')
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(3)

    try:
        page_num = int(driver.find_element(
            By.XPATH, '//*[@id="__layout"]/div/div[2]/section/div[8]/div/nav/ul/li[4]/a').text)
    except Exception:
        page_num = 1

    time.sleep(3)

    tempo = time.monotonic()

    i = 0
    while i <= page_num:

        print(f'A pagina atual é {i}')

        objs = driver.find_elements(
            By.XPATH, '//*[@id="__layout"]/div/div[2]/section/div[9]/div[1]/div/div/div/div/div/article/div/div/p/a')
        time.sleep(2)

        for l in objs:
            try:
                links.append(l.get_attribute('href'))
            except Exception:
                continue

        objs.clear()
        i += 1

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="__layout"]/div/div[2]/section/div[8]/div/nav/a[2]'))).click()
        except Exception:
            pass

    else:
        del objs
        driver.quit()
        diferença = time.monotonic() - tempo
        print(f'A coleta de links durou {diferença} segundos')
        print('Iniciando a coleta de dados...')
        tempo = time.monotonic()

    for link in set(links):

        r = requests.get(link, headers=headers)

        if r.status_code != 200:
            print(
                f'O servidor retornou com o erro de código {r.status_code} para o endereço {link}')
            continue

        soup = BeautifulSoup(r.content, 'html.parser')

        content_keys = [k for k in dados.keys()]

        content = {}

        for k in content_keys:
            try:
                content[k] = soup.find(string=k).parent.find_next_sibling(
                    'p').contents[0].contents[0].strip()
            except Exception:
                try:
                    content[k] = soup.find(string=k).parent.find_next_sibling(
                        'p').contents[0].strip()
                except Exception:
                    content[k] = 'Não informado'

        for k in content.keys():
            dados[k].append(content[k])

        content.clear()

    diferença = time.monotonic() - tempo
    print(f'A coleta de dados durou {diferença} segundos')

    return dados


def main():

    dados = scraping()
    df = pd.DataFrame(data=dados)
    nome = input('Digite o nome que deseja para a planilha: ')
    antes = time.monotonic()
    df.to_csv(nome, index=False)
    agora = time.monotonic() - antes
    print(f'A conversão para .csv durou {agora} segundos.')
    print('Finalizando a execução do script.')
    return 0


if __name__ == '__main__':
    main()
