import glob
#import scipy.io
import numpy as np
from scipy.signal import hilbert
import pyedflib

def correla(pattern, size=None, norm=True, array=True, correlation=True):
    """Essa função recebe o 'pattern' dos arquivos que se deseja estudar e retora dois arrays (ou listas) tridimensionais contendo a correlação e o tau, respectivamente. A primeira dimensão representa cada um dos arquivos, a segunda e a terceira representam os canais.
    Argumento obrigatório:
                          - pattern: string com o padrão para encontrar os aquivos que se deseja estudar. Em caso de dúvida procure informações no README
    Argumentos Opcionais:
                         - norm: booleano. Default 'True'. Retorna a correlação normalizada. Com o argumento norm='False' a correlação não é normalizada
                         - array: booleanp. Default 'True'. Retorna corr e tau como arrays. Com o argumento array='False' os valores retornam como listas"""
    files = glob.glob(pattern) # Cria uma lista com todos os arquivos
    corr = [] #Listas vazias para armazenar corr e tau de todos os arquivos
    tau = []
    for f in files: # Laço sobre todos os arquivos
        clip = pyedflib.EdfReader(f) # Abre cada arquivo
        freq = int(clip.getSampleFrequencies()[0]) # Seleciona a frequência de amostragem
        chan = clip.getSignalLabels() # Transforma os canais em um único array
        nchan = len(chan)
        data = [] # Armazena os dados do arquivo
        for i in range(nchan):
            data_chan = clip.readSignal(i,n=size)
            data.append(data_chan)
        
        corr_clip = [[0 for i in chan] for j in chan] #Cria listas do tamanho adequado para armazenar os valores
        tau_clip = [[0 for i in chan] for j in chan]
        H = hilbert(data) # Transformada de hilbert dos dados
        fase = np.arctan2(np.imag(H),data)
        if correlation:
            fase = np.apply_along_axis(lambda x: x/(x.std()*len(x)),0,fase)
            #print(fase[0])
        for i,fasei in enumerate(fase): #Esses laços varrem todos os canais e armazenam as correlações e taus
            for j,fasej in enumerate(fase):
                c = np.correlate(fasei,fasej,mode='full')
                t = np.argmax(abs(c))
                tau_clip[i][j] = (t-freq+1)/freq # correlação numpy  
                corr_clip[i][j] = c[t]
        if norm:
            corr_diag = []
            for i,ci in enumerate(corr_clip):
                corr_diag.append(ci[i])
            for i in range(nchan): #laço para normalizar
                cii = corr_diag[i]
                for j in range(nchan):
                    cjj = corr_diag[j]
                    corr_clip[i][j] = corr_clip[i][j] / np.sqrt(cii*cjj)
                    
        corr.append(corr_clip) #Armazena a correlação desse arquivo na lista de todos
        tau.append(tau_clip)
        
    if array: #Transforma as listas em arrays
        corr = np.array(corr)    
        tau = np.array(tau)    

    return corr, tau

def escreve_array(array,arquivo):
    """Essa função escreve um array com três dimensões de maneira legível. Pode ser utilizado para escrever um array com um número diferente de dimensões, mas pode comprometer a legibilidade.
    Argumentos obigatórios
                           - array: array que desejamos escrever
                           - arquivo: string com o nome do arquivo de saída"""
    with open(arquivo, 'wb') as f:
        for data_slice in array:
            np.savetxt(f, data_slice, fmt='%f')
            f.write(b'# New slice\n')
