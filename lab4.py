from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from astropy.io import fits 
import matplotlib.pyplot as plt
import numpy as np
import sep
import matplotlib.colors as colors
from scipy.ndimage import maximum_filter
from matplotlib.colors import LogNorm
import astropy.units as u
from astropy.utils import data
data.conf.remote_timeout = 60
from spectral_cube import SpectralCube
from astroquery.esasky import ESASky
from astroquery.utils import TableList
from astropy.wcs import WCS
from reproject import reproject_interp
from flask import send_file
from PIL import Image
import base64
import io
from matplotlib import cm
import time
 
app = Flask(__name__)
upload_folder = os.path.join('static', 'uploads')
app.config['UPLOAD'] = upload_folder
opend_image=''
opend_file=''
opend_hdu=''
colmap = cm.gray 
opend_data = []
@app.route('/', methods=['GET', 'POST'])
def abobik():
    #start_time = time.time()
    global opend_image
    global opend_file
    global opend_hdu
    global colmap
    global opend_data
    if 'solo' in request.form:
        file = request.files['img']
        if file.filename == '':
            return render_template('img_render.html', message='Прикрепите FITS файл')
        filename = secure_filename(file.filename)
        opend_file = os.path.join(app.config['UPLOAD'], filename)
        opend_image = os.path.join(app.config['UPLOAD'], "image.png")
        file.save(opend_file)        
        opend_hdu, data = load_fits(opend_file)
        if data is None:
            opend_hdu, data = load_fits(opend_file,1)
        if data.ndim == 3:
            plt.imshow(data[0, :, :], cmap='gray')
        else:
            plt.imshow(data, cmap='gray', norm=LogNorm())
        colmap = cm.gray
        plt.axis('off')
        plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()
        #end_time = time.time()
        #elapsed_time = end_time - start_time
        #return render_template('img_render.html', img=opend_image, hdu=opend_hdu, message=f"Время выполнения: {elapsed_time:.4f} секунд")
        return render_template('img_render.html', img=opend_image, hdu=opend_hdu)
        
    elif 'sli' in request.form:
        file = request.files['img']
        if file.filename == '':
            return render_template('img_render.html', message='Прикрепите FITS файл')
        filename = secure_filename(file.filename)
        opend_file = os.path.join(app.config['UPLOAD'], filename)
        file.save(opend_file)        
        with fits.open(opend_file) as hdul:
            if hdul[0].data.ndim != 3:
                return render_template('img_render.html', message='Файл не содержит куб данных')
            opend_data = hdul[0].data
            opend_hdu = hdul[0].header
        return render_template('img_render.html', hdu=opend_hdu, message='Файл загружен, проверьте метаданные и выберите ось и место для взятия среза')  
  
    elif 'slicic' in request.form:
        slice_axis = request.form.get('osi')
        slice_index = request.form['os']
        if slice_axis == 'option3':
            slice_data = opend_data[int(slice_index), :, :]
        elif slice_axis == 'option1':
            slice_data = opend_data[:, int(slice_index), :]
        elif slice_axis == 'option2':
            slice_data = opend_data[:, :, int(slice_index)]
        opend_image = os.path.join(app.config['UPLOAD'], "slice.png")
        plt.imshow(slice_data, cmap=colmap)
        plt.axis('off')
        plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()
        return render_template('img_render.html',img=opend_image, hdu=opend_hdu)  
      
    elif 'piki' in request.form:
        file = request.files['img']
        file_d = request.files['img1']
        file_f = request.files['img2']
        if file.filename == '':
            return render_template('img_render.html', message='Прикрепите основной FITS файл')
        if file_d.filename != '' and file_f.filename != '':
            pipe, peaks = piki(file, file_d, file_f)
            opend_image = os.path.join(app.config['UPLOAD'], "image.png")
            filename = secure_filename(file.filename)
            opend_hdu, data = load_fits(os.path.join(app.config['UPLOAD'], filename))
            fig, ax = implot(pipe.image,scale=0.5)
            ax.plot(peaks[:,1],peaks[:,0],'o',color='None',mec='r',ms=10,alpha=0.8);
            plt.axis('off')
            plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            return render_template('img_render.html', img=opend_image, hdu=opend_hdu)
        else:
            filename = secure_filename(file.filename)        
            file.save(os.path.join(app.config['UPLOAD'], filename))
            opend_hdu, data = load_fits(os.path.join(app.config['UPLOAD'], filename))
            peaks = findpeaks_maxfilter(data, threshold=np.mean(data)+3*np.std(data))
            opend_image = os.path.join(app.config['UPLOAD'], "image.png")
            fig, ax = implot(data, scale=0.5)
            ax.plot(peaks[:, 1], peaks[:, 0], 'o', color='None', mec='r', ms=10, alpha=0.8)
            plt.axis('off')
            plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
            #end_time = time.time()
            #elapsed_time = end_time - start_time
            #return render_template('img_render.html', img=opend_image, hdu=opend_hdu,
                                   #message=f'Дополнительные FITS файлы (dark.fits и/или flat.fits) отсутствуют, качество снижено,Время выполнения: {elapsed_time:.4f} секунд')
            return render_template('img_render.html', img=opend_image, hdu=opend_hdu,
                                   message='Дополнительные FITS файлы (dark.fits и/или flat.fits) отсутствуют, качество снижено')
    elif 'kub' in request.form:
        file = request.files['img']
        if file.filename == '':
            return render_template('img_render.html', message='Прикрепите FITS файл с кубом данных')
        filename = secure_filename(file.filename)
        opend_file = os.path.join(app.config['UPLOAD'], filename)
        opend_image = os.path.join(app.config['UPLOAD'], "image.png")
        file.save(filename)
        with fits.open(opend_file) as hdul:
            opend_hdu = hdul[0].header
            if hdul[0].data.ndim != 3:
                return render_template('img_render.html', message='Файл не содержит куб данных')
        kubi(opend_file,opend_image)
        return render_template('img_render.html', img=opend_image, hdu=opend_hdu)
    
    elif 'down' in request.form:
        canvas_data = request.form['canvas_data']
        textarea_data = request.form['story']
        png_file, txt_file = save_files(canvas_data,textarea_data)     
        file_path = png_to_fits(png_file,txt_file)
        return send_file(
            file_path,
            as_attachment=True,
            download_name='xdd.fits'
        ) 
    elif 'cmapsi' in request.form:
        selected_value = request.form.get('cm_selector')
        if selected_value == 'option1':
            colmap = cm.gray
        elif selected_value == 'option2':
            colmap = cm.cool
        elif selected_value == 'option3':
            colmap = cm.hot
        elif selected_value == 'option4':
            colmap = cm.viridis
        elif selected_value == 'option5':
            colmap = cm.magma
        else: 
            colmap = cm.cividis
        img = Image.open(opend_image).convert('L')
        img_array = np.array(img)
        plt.imshow(img_array, cmap=colmap)
        plt.axis('off')
        plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()
        return render_template('img_render.html', img=opend_image, hdu=opend_hdu)
     
    elif 'normaliki' in request.form:
        selected_value = request.form.get('norm_selector')
        if selected_value == 'option1':
            norm = colors.Normalize()
        elif selected_value == 'option2':
            norm = colors.LogNorm()
        elif selected_value == 'option3':
            norm = colors.AsinhNorm()
        elif selected_value == 'option4':
            norm = colors.PowerNorm(gamma=0.5)
        else:
            norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03)
        img = Image.open(opend_image).convert('L')
        img_array = np.array(img)
        plt.imshow(img_array, cmap=colmap, norm=norm)
        plt.axis('off')
        plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()
        return render_template('img_render.html', img=opend_image, hdu=opend_hdu)
    
    elif 'vmin_vmax' in request.form:
        vmin = request.form['min']
        vmax = request.form['max']
        img = Image.open(opend_image).convert('L')
        img_array = np.array(img)
        plt.imshow(img_array, cmap=colmap, vmin=vmin, vmax=vmax)
        plt.axis('off')
        plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()
        return render_template('img_render.html', img=opend_image, hdu=opend_hdu)
 
    else:
        return render_template('img_render.html',img=opend_image, hdu=opend_hdu)

#ФУнкция сохранени в fits
def png_to_fits(png_filepath, txt_filepath):
  try:
    img = Image.open(png_filepath).convert("L")
    img_array = np.array(img)
    header = fits.Header()
    with open(txt_filepath, 'r') as f:
      for line in f:
        line = line.strip()
        if not line or line.startswith('END'):
          continue
        try:
          key, value_comment = line.split('=', 1)
          key = key.strip()
          value_comment = value_comment.strip()
          if '/' in value_comment:
            value, comment = value_comment.split('/', 1)
            value = value.strip()
            comment = comment.strip()
          else:
            value = value_comment.strip()
            comment = None
          if value.upper() == 'T':
            header[key] = True
          elif value.upper() == 'F':
            header[key] = False
          elif value.startswith("'") and value.endswith("'"):
            header[key] = value[1:-1]
          else:
            try:
              header[key] = int(value)
            except ValueError:
              try:
                header[key] = float(value)
              except ValueError:
                header[key] = value
          if comment:
            header.comments[key] = comment # Добавляем комментарий к ключу
        except Exception as e:
          print(f"Ошибка при обработке строки: {line}. Ошибка: {e}")
    hdu = fits.PrimaryHDU(img_array, header=header)
    fits_filepath = "static/uploads/abobik.fits"
    hdu.writeto(fits_filepath, overwrite=True)
    print(f"FITS файл успешно создан: {fits_filepath}")
  except FileNotFoundError:
    print("Ошибка: Один из файлов не найден.")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  return fits_filepath

#функция сохранения файлов
def save_files(canvas_data, textarea_data):
    can_path = "static/uploads/canvas.png"
    meta_path = "static/uploads/meta.txt"
    try:
        if not canvas_data:
            print("Предупреждение: Данные canvas пустые.  Изображение не будет сохранено.")
        else:
            if canvas_data.startswith("data:image/png;base64,"):
                canvas_data = canvas_data[len("data:image/png;base64,"):]
            image_data = base64.b64decode(canvas_data)
            image = Image.open(io.BytesIO(image_data))
            image.save(can_path, "PNG")
            print("Изображение из canvas сохранено")
    except Exception as e:
        print(f"Ошибка при сохранении изображения из canvas: {e}")      
    try:
        if textarea_data.startswith('"') and textarea_data.endswith('"'):
            trimmed_text = textarea_data[1:-1]  # Обрезаем первый и последний символ
        else:
            trimmed_text = textarea_data
        with open(meta_path, "w", encoding="utf-8") as f:  # Явно указываем кодировку UTF-8
            f.write(trimmed_text)
        print("Текст из textarea сохранен")
    except Exception as e:
        print(f"Ошибка при сохранении текста из textarea: {e}")
    return can_path, meta_path


#Функция открытия файла
def load_fits(fpath,extension=0):
    with fits.open(fpath) as hdu:
        header = hdu[extension].header
        data = hdu[extension].data
    return header, data

#Функция отрисовки пиков (кажется)
def implot(image,figsize=(15,13),cmap='gray_r',scale=0.5,**kwargs):
    fig, ax = plt.subplots(figsize=figsize)
    mu = np.mean(image)
    s = np.std(image)
    plt.rcParams.update({'font.size': 9})
    dvmin = mu - scale*s
    dvmax = mu + scale*s
    if all(['vmin','vmax']) in kwargs.keys():
        ax.imshow(image,origin='lower',cmap=cmap,vmin=kwargs['vmin'],vmax=kwargs['vmax'])
    elif 'vmin' in kwargs.keys():
        ax.imshow(image,origin='lower',cmap=cmap,vmin=kwargs['vmin'],vmax=dvmax)
    elif 'vmax' in kwargs.keys():
        ax.imshow(image,origin='lower',cmap=cmap,vmin=dvmin,vmax=kwargs['vmax'])
    else:
        ax.imshow(image,origin='lower',cmap=cmap,vmin=dvmin,vmax=dvmax)
    return fig, ax

#Класс для работы с пиками 
class PSFPhot():
    def __init__(self,data_fpath,dark_fpath,flat_fpath):
        self.data_header, self.data_init = load_fits(data_fpath)
        self.data_calibrated = self.flat_field(self.dark_subtract(self.data_init,dark_fpath),flat_fpath)
    def dark_subtract(self,image,dark_path):
        h,dark_im = load_fits(dark_path)
        return np.subtract(image,dark_im)
    def flat_field(self,image,flat_path):
        h,flat_im = load_fits(flat_path)
        flat_im/=np.max(flat_im)
        return image/flat_im
    def subtract_background(self,mask=None):
        data_corder = self.data_calibrated.copy(order='C')
        bkg = sep.Background(data_corder, mask=mask)
        self.background = bkg.back()
        self.image = self.data_calibrated - self.background
        print('Background estimated; output saved to attribute image')
    def set_image_mask(self,mask=None):
        if hasattr(self,'image'):
            self.image = np.ma.masked_array(self.image,mask=mask)
        else:
            self.image = np.ma.masked_array(self.data_calibrated,mask=mask)
    def findpeaks_maxfilter(self,threshold=0):
            neighborhood = np.ones((3,3),dtype=bool)
            amax = maximum_filter(self.image, footprint=neighborhood)
            peaks = np.where((self.image == amax) & (self.image >= threshold))
            peaks = np.array([peaks[0],peaks[1]]).T
            out_peaks = []
            for i in peaks:
                peak_flux = self.image[i[0],i[1]]
                mini_cutout = self.image[i[0]-1:i[0]+2,i[1]-1:i[1]+2]
                accept = np.where(mini_cutout>0.5*peak_flux)
                if len(accept[0]) > 7:
                    out_peaks.append(i)
            return np.array(out_peaks)

def findpeaks_maxfilter(image, threshold=0):
    neighborhood = np.ones((3, 3), dtype=bool)
    amax = maximum_filter(image, footprint=neighborhood)
    peaks = np.where((image == amax) & (image >= threshold))
    peaks = np.array([peaks[0], peaks[1]]).T
    out_peaks = []
    for i in peaks:
        peak_flux = image[i[0], i[1]]
        mini_cutout = image[i[0] - 1:i[0] + 2, i[1] - 1:i[1] + 2]
        accept = np.where(mini_cutout > 0.5 * peak_flux)
        if len(accept[0]) > 7:
            out_peaks.append(i)
    return np.array(out_peaks)
#ФУнкция для пиков
def piki(file,file_d,file_f):
    filename = secure_filename(file.filename)        
    file.save(os.path.join(app.config['UPLOAD'], filename))
    filename_d = secure_filename(file_d.filename)
    file_d.save(os.path.join(app.config['UPLOAD'], filename_d))
    filename_f = secure_filename(file_f.filename)
    file_f.save(os.path.join(app.config['UPLOAD'], filename_f))
      
    pipe = PSFPhot(os.path.join(app.config['UPLOAD'], filename), 
                   dark_fpath=os.path.join(app.config['UPLOAD'], filename_d), 
                   flat_fpath=os.path.join(app.config['UPLOAD'], filename_f))
    pipe.subtract_background()
    pipe.set_image_mask()
    peaks = pipe.findpeaks_maxfilter(threshold=np.mean(pipe.image)+3*np.std(pipe.image))
    return  pipe, peaks

#Функция для работы с кубами
def kubi(file,opend_image):
    hi_data = fits.open(file)
    cube = SpectralCube.read(hi_data)  
    hi_data.close() 
    lat_range = [-46, -40] * u.deg 
    lon_range = [306, 295] * u.deg
    sub_cube = cube.subcube(xlo=lon_range[0], xhi=lon_range[1], ylo=lat_range[0], yhi=lat_range[1])
    sub_cube_slab = sub_cube.spectral_slab(-300. *u.km / u.s, 300. *u.km / u.s)
    moment_0 = sub_cube_slab.with_spectral_unit(u.km/u.s).moment(order=0) 
    moment_1 = sub_cube_slab.with_spectral_unit(u.km/u.s).moment(order=1)
    hi_column_density = moment_0 * 1.82 * 10**18 / (u.cm * u.cm) * u.s / u.K / u.km
    result = ESASky.query_region_maps('SMC', radius=1*u.deg, missions='Herschel')
    filters = result['HERSCHEL']['filter'].astype(str)
    mask = np.array(['250, 350, 500' == s for s in filters], dtype='bool')
    target_obs = TableList({"HERSCHEL":result['HERSCHEL'][mask]})
    IR_images = ESASky.get_maps(target_obs)
    herschel_header = IR_images['HERSCHEL'][0]['350']['image'].header
    herschel_imagehdu = IR_images['HERSCHEL'][0]['350']['image'] 
    himage_nan_locs = np.isnan(herschel_imagehdu.data)
    herschel_data_nonans = herschel_imagehdu.data
    herschel_data_nonans[himage_nan_locs] = 0
    rescaled_herschel_data, _ = reproject_interp(herschel_imagehdu, hi_column_density.hdu.header) 
    rescaled_herschel_imagehdu = fits.PrimaryHDU(data = rescaled_herschel_data, header = hi_column_density.hdu.header)
    image_nan_locs = np.isnan(rescaled_herschel_imagehdu.data)
    rescaled_herschel_data_nonans = rescaled_herschel_imagehdu.data
    rescaled_herschel_data_nonans[image_nan_locs] = 0
    fig = plt.figure(figsize = (18,12))
    ax = fig.add_subplot(111,projection = WCS(rescaled_herschel_imagehdu))
    im = ax.imshow(rescaled_herschel_data_nonans, cmap = 'viridis', norm = LogNorm(vmin=5, vmax=50), alpha = .8)
    ax.invert_yaxis()
    ax.set_xlabel("Galactic Longitude", fontsize = 20)
    ax.set_ylabel("Galactic Latitude", fontsize = 20)
    ax.grid(color = 'white', ls = 'dotted', lw = 2)
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()
    cbar = plt.colorbar(im, fraction=0.046, pad=0.05)
    cbar.set_label(''.join(['Herschel 350'r'$\mu$m ','(', herschel_header['BUNIT'], ')']), size = 20)
    overlay = ax.get_coords_overlay('fk5')
    overlay.grid(color='black', ls='dotted', lw = 1)
    overlay[0].set_axislabel('Right Ascension', fontsize = 20)
    overlay[1].set_axislabel('Declination', fontsize = 20)
    hi_transform = ax.get_transform(hi_column_density.wcs)
    levels = (2e21, 3e21, 5e21, 7e21, 8e21, 1e22)
    ax.contour(hi_column_density.hdu.data, cmap = 'Greys_r', alpha = 0.8, levels = levels,transform = hi_transform)
    im_hi = ax.imshow(moment_1.hdu.data, cmap = 'RdBu_r', vmin = 0, vmax = 200, alpha = 0.5, transform = hi_transform)
    cbar_hi = plt.colorbar(im_hi, orientation = 'horizontal', fraction=0.046, pad=0.07)
    cbar_hi.set_label('HI 'r'$21$cm Mean Velocity (km/s)', size = 20)
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    plt.rcParams.update({'font.size': 11})
    plt.savefig(opend_image, bbox_inches='tight', pad_inches=0, dpi=300)
    return
 
if __name__ == '__main__':
    app.run(debug=True, port=8001)