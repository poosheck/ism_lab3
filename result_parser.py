import json
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def get_reggresion_arrays(list1, list2):

    gradient, intercept, r_value, p_value, std_err = stats.linregress(list1, list2)

    mn = np.min(list1)
    mx = np.max(list1)

    x1 = np.linspace(mn, mx, 500)
    y1 = gradient * x1 + intercept

    return x1, y1

def plot_mos(results):
    scatter_guitar_x = []
    scatter_orchestral_x = []
    scatter_voice_x = []

    scatter_guitar_y = []
    scatter_orchestral_y = []
    scatter_voice_y = []

    for i in results:
            if i['Clip'] == './guitar_mono.wav':
                scatter_guitar_y.append(i['PSNR'])
                scatter_guitar_x.append(i['Score'])
            if i['Clip'] == './orchestral_mono.wav':
                scatter_orchestral_y.append(i['PSNR'])
                scatter_orchestral_x.append(i['Score'])
            if i['Clip'] == './voice_mono.wav':
                scatter_voice_y.append(i['PSNR'])
                scatter_voice_x.append(i['Score'])


    all_scatter_x = scatter_guitar_x + scatter_orchestral_x + scatter_voice_x
    all_scatter_y = scatter_guitar_y + scatter_orchestral_y + scatter_voice_y
    zipped_lists = zip(all_scatter_x, all_scatter_y)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    list1, list2 = [list(tuple) for tuple in tuples]

    regg_all = get_reggresion_arrays(list1, list2)
    regg_guitar = get_reggresion_arrays(scatter_guitar_x, scatter_guitar_y)
    regg_orchestral = get_reggresion_arrays(scatter_orchestral_x, scatter_orchestral_y)
    regg_voice = get_reggresion_arrays(scatter_voice_x, scatter_voice_y)

    plt.figure()
    plt.plot(scatter_guitar_x, scatter_guitar_y, 'r*')
    plt.plot(regg_guitar[0], regg_guitar[1], '--r', label='Guitar')
    plt.plot(scatter_orchestral_x, scatter_orchestral_y, 'g*')
    plt.plot(regg_orchestral[0], regg_orchestral[1], '--g', label='Orchestral')
    plt.plot(scatter_voice_x, scatter_voice_y, 'b*')
    plt.plot(regg_voice[0], regg_voice[1], '--b', label='Voice')
    plt.plot(regg_all[0], regg_all[1], '-k', label='All')
    plt.xlabel('Score')
    plt.ylabel('PSNR')
    plt.legend()

def plot_compression(results):
    scatter_guitar_x_str = []
    scatter_orchestral_x_str = []
    scatter_voice_x_str = []

    scatter_guitar_x = []
    scatter_orchestral_x = []
    scatter_voice_x = []

    scatter_guitar_y = []
    scatter_orchestral_y = []
    scatter_voice_y = []

    for i in results:
        if i['Bitdepth'] == 16 and i['Frequency'] == 44100 and i['PSNR'] != 100:

            if i['Clip'] == './guitar_mono.wav':
                scatter_guitar_y.append(i['PSNR'])
                scatter_guitar_x_str.append(i['Compression'])
            if i['Clip'] == './orchestral_mono.wav':
                scatter_orchestral_y.append(i['PSNR'])
                scatter_orchestral_x_str.append(i['Compression'])
            if i['Clip'] == './voice_mono.wav':
                scatter_voice_y.append(i['PSNR'])
                scatter_voice_x_str.append(i['Compression'])

    for i in scatter_guitar_x_str:
        if i == "a-LAW":
            scatter_guitar_x.append(2)
        if i == "u-LAW":
            scatter_guitar_x.append(4)
        if i == "ADPCM":
            scatter_guitar_x.append(6)

    for i in scatter_orchestral_x_str:
        if i == "a-LAW":
            scatter_orchestral_x.append(2)
        if i == "u-LAW":
            scatter_orchestral_x.append(4)
        if i == "ADPCM":
            scatter_orchestral_x.append(6)

    for i in scatter_voice_x_str:
        if i == "a-LAW":
            scatter_voice_x.append(2)
        if i == "u-LAW":
            scatter_voice_x.append(4)
        if i == "ADPCM":
            scatter_voice_x.append(6)

    all_scatter_x = scatter_guitar_x + scatter_orchestral_x + scatter_voice_x
    all_scatter_y = scatter_guitar_y + scatter_orchestral_y + scatter_voice_y
    zipped_lists = zip(all_scatter_x, all_scatter_y)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    list1, list2 = [list(tuple) for tuple in tuples]

 #   regg_all = get_reggresion_arrays(list1, list2)
 #   regg_guitar = get_reggresion_arrays(scatter_guitar_x, scatter_guitar_y)
 #   regg_orchestral = get_reggresion_arrays(scatter_orchestral_x, scatter_orchestral_y)
 #   regg_voice = get_reggresion_arrays(scatter_voice_x, scatter_voice_y)

    plt.figure()
    plt.plot(scatter_guitar_x, scatter_guitar_y, 'r*', label='Guitar')
 #   plt.plot(regg_guitar[0], regg_guitar[1], '--r')
    plt.plot(scatter_orchestral_x, scatter_orchestral_y, 'g*', label='Orchestral')
  #  plt.plot(regg_orchestral[0], regg_orchestral[1], '--g')
    plt.plot(scatter_voice_x, scatter_voice_y, 'b*', label='Voice')
  #  plt.plot(regg_voice[0], regg_voice[1], '--b')
  #  plt.plot(regg_all[0], regg_all[1], '-k')
    plt.legend()
    plt.xlabel('Compression')
    plt.ylabel('PSNR')
    plt.text(2, 40, 'a-LAW')
    plt.text(4, 40, 'u-LAW' ,horizontalalignment='right')
    plt.text(6, 40, 'ADPCM' ,horizontalalignment='right')

def plot_frequency(results):
    scatter_guitar_x = []
    scatter_orchestral_x = []
    scatter_voice_x = []

    scatter_guitar_y = []
    scatter_orchestral_y = []
    scatter_voice_y = []

    for i in results:
        if i['Bitdepth'] == 16 and i['Compression'] == 'None' and i['PSNR'] != 100:

            if i['Clip'] == './guitar_mono.wav':
                scatter_guitar_y.append(i['PSNR'])
                scatter_guitar_x.append(i['Frequency'])
            if i['Clip'] == './orchestral_mono.wav':
                scatter_orchestral_y.append(i['PSNR'])
                scatter_orchestral_x.append(i['Frequency'])
            if i['Clip'] == './voice_mono.wav':
                scatter_voice_y.append(i['PSNR'])
                scatter_voice_x.append(i['Frequency'])


    all_scatter_x = scatter_guitar_x + scatter_orchestral_x + scatter_voice_x
    all_scatter_y = scatter_guitar_y + scatter_orchestral_y + scatter_voice_y
    zipped_lists = zip(all_scatter_x, all_scatter_y)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    list1, list2 = [list(tuple) for tuple in tuples]

    regg_all = get_reggresion_arrays(list1, list2)
    regg_guitar = get_reggresion_arrays(scatter_guitar_x, scatter_guitar_y)
    regg_orchestral = get_reggresion_arrays(scatter_orchestral_x, scatter_orchestral_y)
    regg_voice = get_reggresion_arrays(scatter_voice_x, scatter_voice_y)

    plt.figure()
    plt.plot(scatter_guitar_x, scatter_guitar_y, 'r*')
    plt.plot(regg_guitar[0], regg_guitar[1], '--r', label='Guitar')
    plt.plot(scatter_orchestral_x, scatter_orchestral_y, 'g*')
    plt.plot(regg_orchestral[0], regg_orchestral[1], '--g', label='Orchestral')
    plt.plot(scatter_voice_x, scatter_voice_y, 'b*')
    plt.plot(regg_voice[0], regg_voice[1], '--b', label='Voice')
    plt.plot(regg_all[0], regg_all[1], '-k', label='All')
    plt.xlabel('Frequency')
    plt.ylabel('PSNR')
    plt.legend()

def plot_bitdepth(results):
    scatter_guitar_x = []
    scatter_orchestral_x = []
    scatter_voice_x = []

    scatter_guitar_y = []
    scatter_orchestral_y = []
    scatter_voice_y = []

    for i in results:
        if i['Frequency'] == 44100 and i['Compression'] == 'None' and i['PSNR'] != 100:

            if i['Clip'] == './guitar_mono.wav':
                scatter_guitar_y.append(i['PSNR'])
                scatter_guitar_x.append(i['Bitdepth'])
            if i['Clip'] == './orchestral_mono.wav':
                scatter_orchestral_y.append(i['PSNR'])
                scatter_orchestral_x.append(i['Bitdepth'])
            if i['Clip'] == './voice_mono.wav':
                scatter_voice_y.append(i['PSNR'])
                scatter_voice_x.append(i['Bitdepth'])


    all_scatter_x = scatter_guitar_x + scatter_orchestral_x + scatter_voice_x
    all_scatter_y = scatter_guitar_y + scatter_orchestral_y + scatter_voice_y
    zipped_lists = zip(all_scatter_x, all_scatter_y)
    sorted_pairs = sorted(zipped_lists)
    tuples = zip(*sorted_pairs)
    list1, list2 = [list(tuple) for tuple in tuples]


    regg_all = get_reggresion_arrays(list1, list2)

    plt.figure()
    plt.plot(scatter_guitar_x, scatter_guitar_y, 'r*', label='Guitar')
    plt.plot(scatter_orchestral_x, scatter_orchestral_y, 'g*', label='Orchestral')
    plt.plot(scatter_voice_x, scatter_voice_y, 'b*', label='Voice')
    plt.plot(regg_all[0], regg_all[1], '-k', label='All')
    plt.xlabel('Bitdepth')
    plt.ylabel('PSNR')
    plt.legend()

if __name__ == "__main__":
    with open("./results.json", 'r') as f:
        results = json.load(f)

    plot_bitdepth(results)
    plot_frequency(results)
    plot_compression(results)
    plot_mos(results)
    plt.show()
