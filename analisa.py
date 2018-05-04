from correla_fase import correla,escreve_array
import numpy as np

#
# pattern seleciona quais arquivos pretende acessar.
#
pattern = '../chb01/*01.edf' 

corr, tau = correla(pattern,500) 

escreve_array(np.stack((corr[0],tau[0])), 'corr.dat')
