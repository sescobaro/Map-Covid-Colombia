import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import re
import os
import gc
import imageio


#13001 Cartagena, #13 Bolívar
#8001 Barranquilla, #8 Atlántico
#47001 Santa Marta, #47 Magdalena


df = pd.read_csv(r'Casos_positivos_de_COVID-19_en_Colombia.csv')
df.columns

#'8,001', '47,001' and '13,001' are special districts within a department, code will be replaced for the department code
df['Código DIVIPOLA departamento']=df['Código DIVIPOLA departamento'].replace('13,001', 13)
df['Código DIVIPOLA departamento']=df['Código DIVIPOLA departamento'].replace('8,001', 8)
df['Código DIVIPOLA departamento']=df['Código DIVIPOLA departamento'].replace('47,001', 47)

#Produciendo un df más pequeño
df_1=df[['fecha reporte web', 'Código DIVIPOLA departamento', 'Nombre departamento', 
         'Fecha de muerte', 'Fecha de recuperación']]
df_1.head()

#Modificando la fecha de df_1
time = df_1['fecha reporte web'].values

dia=[]
mes=[]
año=[]
d_time=[]

for date in time:
    day=int(date[8:10])
    dia.append(day)
    month=int(date[5:7])
    mes.append(month)
    year=int(date[0:4])
    año.append(year)
    d_time.append(datetime.date(year, month, day))
    
df_1['fecha reporte web']=d_time

#Modificando la fecha de recuperación de df_1
time = df_1['Fecha de recuperación'].values

dia=[]
mes=[]
año=[]
d_time=[]

for date in time:
    if type(date) == str:
        day=int(date[8:10])
        dia.append(day)
        month=int(date[5:7])
        mes.append(month)
        year=int(date[0:4])
        año.append(year)
        d_time.append(datetime.date(year, month, day))
    else:
        d_time.append('')
    
df_1['Fecha de recuperación']=d_time

#Modificando la fecha de muerte de df_1
time = df_1['Fecha de muerte'].values

dia=[]
mes=[]
año=[]
d_time=[]

for date in time:
    if type(date) == str:
        day=int(date[8:10])
        dia.append(day)
        month=int(date[5:7])
        mes.append(month)
        year=int(date[0:4])
        año.append(year)
        d_time.append(datetime.date(year, month, day))
    else:
        d_time.append('')
    
df_1['Fecha de muerte']=d_time



#Lista de códigos únicos
list_dep_df=df_1['Código DIVIPOLA departamento'].unique()


# #Contabilizando el total de casos por departamento
# total_dep=df_1.groupby('Código DIVIPOLA departamento')['fecha reporte web'].count()

# #Pasando el total de casos a df y haciendo del index una columna
# total_dep=total_dep.to_frame()
# total_dep=total_dep.rename(columns={'fecha reporte web':'Total'})
# total_dep['Código DIVIPOLA departamento']=total_dep.index
# total_dep.dtypes
# #total_dep=total_dep.reset_index(level=0, drop=True)

#
start = min(df_1["fecha reporte web"])
end = max(df_1["fecha reporte web"])

seqDates = []

d = start
while d <= end:
    seqDates.append(d)
    d += datetime.timedelta(days=1)

dff=pd.DataFrame(seqDates)
dff.columns=['Fecha']

#Importando datos de población por departamento
df_pob=pd.read_excel(r'Pob_departamentos.xlsx')

t_pob=[]
for i in df_pob['Población Total']:
    i=re.sub(r"\s+", "", i)
    t_pob.append(int(i))
    
df_pob['Población Total']=t_pob
df_pob=df_pob.set_index('Departamento')
df_pob=df_pob['Población Total']

#Generando un df por cada código único
i=0
for dep in list_dep_df:
    globals()[f'df_dep{i}']=df_1[df_1['Código DIVIPOLA departamento']==dep]
    globals()[f'df_dep{i}']=globals()[f'df_dep{i}'].reset_index(level=0, drop=True)
    #Se suman y se resume al total de casos reportados ese día
    test=globals()[f'df_dep{i}'].groupby('fecha reporte web').count()
    test=test['Código DIVIPOLA departamento']
    test2=globals()[f'df_dep{i}'].groupby('Fecha de recuperación').count()
    test2=test2['Código DIVIPOLA departamento']
    test3=globals()[f'df_dep{i}'].groupby('Fecha de muerte').count()
    test3=test3['Código DIVIPOLA departamento']
    n_casos=[]
    for row in dff['Fecha']:
        if row in globals()[f'df_dep{i}']['fecha reporte web'].values:
            #n_casos.append(test[test['fecha'] == row])
            x=(test[test.index == row])
            n_casos.append(x[0])
        else:
            n_casos.append(0)
    n_recuperados=[]
    for row in dff['Fecha']:
        if row in globals()[f'df_dep{i}']['Fecha de recuperación'].values:
            #n_casos.append(test[test['fecha'] == row])
            x=(test2[test2.index == row])
            n_recuperados.append(x[0])
        else:
            n_recuperados.append(0)
    n_muertos=[]
    for row in dff['Fecha']:
        if row in globals()[f'df_dep{i}']['Fecha de muerte'].values:
            #n_casos.append(test[test['fecha'] == row])
            x=(test3[test3.index == row])
            n_muertos.append(x[0])
        else:
            n_muertos.append(0)
    
    t_casos=[]
    w=0
    tot=0
    while w < len(n_casos):
        tot = tot+n_casos[w]
        t_casos.append(tot)
        w=w+1
    
    t_recuperados=[]
    w=0
    tot=0
    while w < len(n_casos):
        tot = tot+n_recuperados[w]
        t_recuperados.append(tot)
        w=w+1
    
    t_muertos=[]
    w=0
    tot=0
    while w < len(n_casos):
        tot = tot+n_muertos[w]
        t_muertos.append(tot)
        w=w+1
    
    c_activos=[]
    w=0
    while w < len(t_casos):
        tot = t_casos[w]-(t_recuperados[w]+t_muertos[w])
        c_activos.append(tot)
        w=w+1
    
    dep
    dep=int(dep)

    pob=df_pob[df_pob.index == dep]
    c_activos_pm=[]
    for item in c_activos:
        x=(item/pob[dep])*100000
        c_activos_pm.append(x)
            
    globals()[f'dff_{i}']=pd.DataFrame(seqDates)
    globals()[f'dff_{i}'].columns=['Fecha']
    globals()[f'dff_{i}'][dep]=c_activos_pm
    globals()[f'dff_{i}']=globals()[f'dff_{i}'].set_index('Fecha')
    globals()[f'dff_{i}']=globals()[f'dff_{i}'].T
    i=i+1


dff_final=dff_0
for i in range(1, len(list_dep_df)):
    dff_final=dff_final.append(globals()[f'dff_{i}'])

# set the filepath and load in a shapefile
fp = r'MGN2020_00_COLOMBIA\ADMINISTRATIVO\MGN_DPTO_POLITICO.shp'
map_df = gpd.read_file(fp)
map_df.dtypes

for row in map_df['DPTO_CCDGO']:
    map_df['DPTO_CCDGO']=map_df['DPTO_CCDGO'].replace(row, int(row))

map_df = map_df.set_index('DPTO_CCDGO')


df_dep = map_df.join(dff_final)

dfcol=df_dep.columns
dfcol=dfcol[30:]


############### Gráfico ###############

# CREATE A LOOP TO MAKE MULTIPLE MAPS WITH YEAR ANNOTATIONS

# save all the maps in the charts folder
output_path = 'Maps'

# counter for the for loop
i = 0

# list of years (which are the column names at the moment)
list_of_years = dfcol

# set the min and max range for the choropleth map
vmin, vmax = 0, 800

# start the for loop to create one map per year
for year in list_of_years:
    
    # create map
    fig = df_dep.plot(column=year, cmap='Purples', figsize=(10,10), linewidth=0.8, edgecolor='0.8', vmin=vmin, vmax=vmax, 
                       legend=True, norm=plt.Normalize(vmin=vmin, vmax=vmax)) # UDPATE: added plt.Normalize to keep the legend range the same for all maps
    
    # remove axis of chart
    fig.axis('off')
    
    # add a title
    fig.set_title('Casos activos por cada 100.000 hab.', \
              fontdict={'fontsize': '25',
                         'fontweight' : '3'})
    
    # create an annotation for the year
    only_year = str(year)
    
    # position the annotation to the bottom left
    fig.annotate(only_year,
            xy=(0.1, .225), xycoords='figure fraction',
            horizontalalignment='left', verticalalignment='top',
            fontsize=21)
    
    # Another anotation for source
    fig.annotate('Source: Instituto Nacional de Salud (INS)',
            xy=(0.1, .1), xycoords='figure fraction',
            horizontalalignment='left', verticalalignment='top',
            fontsize=16)


    # this will save the figure as a high-res png in the output path. you can also save as svg if you prefer.
    filepath = os.path.join(output_path, only_year+'_c_activos.png')
    chart = fig.get_figure()
    chart.savefig(filepath, dpi=250)
    plt.close('all')
    gc.collect()

#Making a gif
png_dir = 'Maps'
images = []
for file_name in sorted(os.listdir(png_dir)):
    if file_name.endswith('.png'):
        file_path = os.path.join(png_dir, file_name)
        images.append(imageio.imread(file_path))
imageio.mimsave('movie.gif', images, fps=10)





# ############### Gráfico ###############

# # set the range for the choropleth
# vmin, vmax = (min(df_dep['Total'])*0.5, max(df_dep['Total']*0.8))

# # create figure and axes for Matplotlib
# fig, ax = plt.subplots(1, figsize=(10, 6))

# # create map
# df_dep.plot(df_dep['Total'], cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')

# # Now we can customise and add annotations

# # remove the axis
# ax.axis('off')

# # add a title
# ax.set_title('Total de casos por departamento', \
#               fontdict={'fontsize': '25',
#                         'fontweight' : '3'})

# # create an annotation for the  data source
# ax.annotate('Source: Instituto Nacional de Salud (INS)',
#            xy=(0.1, .08), xycoords='figure fraction',
#            horizontalalignment='left', verticalalignment='top',
#            fontsize=10, color='#555555')

# # Create colorbar as a legend
# sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# sm._A = []
# cbar = fig.colorbar(sm)

# # this will save the figure as a high-res png. you can also save as svg
# fig.savefig('test', dpi=400)
# fig.show()
