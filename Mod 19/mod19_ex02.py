# Imports
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from PIL                 import Image
from io                  import BytesIO

# Função para ler os dados
@st.cache_resource(show_spinner= True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)
    # Função para converter o df para csv
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer._save()
    processed_data = output.getvalue()
    return processed_data

# Função para filtrar baseado na multiseleção de categorias
@st.cache_resource
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função principal da aplicação
def main():
    # Configuração inicial da página da aplicação
    st.set_page_config(page_title = 'Telemarketing analisys', \
        page_icon = '../img/telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded'
    )

    # Título principal da aplicação
    st.write('# Telemarketing analisys')
    st.markdown("---")
    
    # Apresenta a imagem na barra lateral da aplicação
    image = Image.open("../img/Bank-Branding.jpg")
    st.sidebar.image(image)

    # Botão para carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type = ['csv','xlsx'])

    # Verifica se há conteúdo carregado na aplicação
    if (data_file_1 is not None):
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())
                   
        with st.sidebar.form(key='my_form'):
            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade', 
                                        min_value = min_age,
                                        max_value = max_age, 
                                        value = (min_age, max_age),
                                        step = 1)
            #DURAÇÃO
            max_duration = int(bank.duration.max())
            min_duration = int(bank.duration.min())
            duracao = st.slider(label='Duração', 
                                        min_value = min_duration,
                                        max_value = max_duration, 
                                        value = (min_duration, max_duration),
                                        step = 1)


            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])

            
            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            
            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])

            
            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])

            
            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Mês do contato", month_list, ['all'])

            
            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # POUTCOME?
            poutcome_list = bank.poutcome.unique().tolist()
            poutcome_list.append('all')
            poutcome_selected = st.multiselect("Poutcome",poutcome_list,['all'])

            # YES?
            y_list = bank.y.unique().tolist()
            y_list.append('all')
            y_selected = st.multiselect("Yes",y_list,['all'])
                    
            # encadeamento de métodos para filtrar a seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .query("duration >= @duracao[0] and duration <= @duracao[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                        .pipe(multiselect_filter, 'poutcome', poutcome_selected)
                        .pipe(multiselect_filter, 'y', y_selected)
            )


            submit_button = st.form_submit_button(label='Aplicar')    
        
        # Botões de download dos dados filtrados
        st.write('## Após os filtros')
        st.write(bank.head())
        
        df_xlsx = to_excel(bank)
        st.download_button(label='📥 Download tabela filtrada em EXCEL',
                            data=df_xlsx ,
                            file_name= 'bank_filtered.xlsx')
        st.markdown("---")
        
        # PLOTS    
        fig, ax = plt.subplots(1, 2, figsize = (5,3))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize = True).to_frame()*100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()
        
        try:
            bank_target_perc = bank.y.value_counts(normalize = True).to_frame()*100
            bank_target_perc = bank_target_perc.sort_index()
        except:
            st.error('Erro no filtro')


        # Botões de download dos dados dos gráficos
        col1, col2 = st.columns(2)

        df_xlsx = to_excel(bank_raw_target_perc)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='📥 Download',
                            data=df_xlsx ,
                            file_name= 'bank_raw_y.xlsx')
        
        df_xlsx = to_excel(bank_target_perc)
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button(label='📥 Download',
                            data=df_xlsx ,
                            file_name= 'bank_y.xlsx')
        st.markdown("---")
    

if __name__ == '__main__':
	main()