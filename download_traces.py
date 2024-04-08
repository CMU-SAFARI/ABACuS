import wget

url = 'https://zenodo.org/records/10575683/files/abacus_cputraces.tar.bz2?download=1'

wget.download(url, 'cputraces.tar.bz2')


