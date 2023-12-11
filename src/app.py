import pandas as pd
import streamlit as st
import scipy.stats as stats
import plotly.graph_objects as go


def shapiro(data_1, data_2):
    stat_shapiro_1, p_1 = stats.shapiro(data_1)
    stat_shapiro_2, p_2 = stats.shapiro(data_2)
    st.text(f'Выборка 1: Статистика Шапиро={stat_shapiro_1:.3f}, p-value={p_1:.3f}')
    st.text(f'Выборка 2: Статистика Шапиро={stat_shapiro_2:.3f}, p-value={p_2:.3f}')
    if p_1 > 0.05 and p_2 > 0.05:
        st.text(f'Результат: Принять гипотезу о нормальности обоих распределений\n')
        test_n=1
    else:
        st.text(f'Результат: Отклонить гипотезу о нормальности обоих распределений\n')
        test_n=0
    return test_n


def mannwhitgreater(data_1, data_2, alpha):
    stat_mw, p_value_mw = stats.mannwhitneyu(data_1, data_2, alternative='greater')
    st.text(f'Статистика Манна-Уитни={stat_mw :.3f}, p-value={p_value_mw:.3f}')
    if p_value_mw < alpha:
        st.text(f'Отклоняем нулевую гипотезу о том, что выборки 1 и 2 не отличаются на уровне значимости {alpha}')
        st.text('Принимаем альтернативную одностороннюю гипотезу о том, среднее выборки 1 больше')
        result=1
        
    else:
        st.text(f'Принимаем нулевую гипотезу о том, что выборки 1 и 2 не отличаются на уровне значимости {alpha}')
        result=0
    return result
        



st.markdown(
    "<h3 style='text-align: center; color: red;'>Сервис проверки статистических гипотез</h3>",
    unsafe_allow_html=True
)
# загрузка данных
uploaded_file = st.file_uploader("Выберите файл .csv", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='1251', sep=',', quoting=3)
    df = df.astype(str).map(lambda x: x.replace('"', ''))
    df.columns=['sick_days', 'age', 'gender']
    df[['age','sick_days']]= df[['age','sick_days']].astype(int)
    maxdays=df['sick_days'].max()
    minage=df['age'].min()
    maxage=df['age'].max()


    # задание параметров age и work_days, ввод параметров
    work_days = st.slider("Выберите порог пропущенных рабочих дней", min_value=0, max_value=maxdays, value=2, step=1)
    age = st.slider("Выберите возрастной порог", min_value=minage, max_value=maxage, value=35, step=1)
    df = df[df['sick_days'] > work_days]


    st.subheader('Гипотезы')
    st.text("Сервис проверит следующие гипотезы при уровне значимости 0.05:")
    st.write(f"1. Мужчины пропускают в течение года более {work_days} дней по болезни значимо чаще женщин.")
    st.write(f"2. Работники старше {age} лет пропускают в течение года более {work_days} дней  по болезни по болезни значимо чаще своих более молодых коллег.")
    alpha = 0.05
    if st.button('Проверить гипотезу 1'):
        # фильтрация данных для проверки гипотезы 1
        data_male = df[df['gender'] == 'М']['sick_days'].sort_values()
        data_female = df[df['gender'] == 'Ж']['sick_days'].sort_values()
        st.subheader('Выборки')
        st.text(f"Выборка 1: Сотрудники мужчины, пропустившиее более {work_days} дней по болезни,\nобъем выборки - {len(data_male)}")
        st.text (f"\nВыборка 2: Сотрудники женщины, пропустившиее более {work_days} дней по болезни,\nобъем выборки -  {len(data_female)}")

        #Проверка достаточного объема выборок
        if (len(data_male)<3 or len(data_female)<3):
            st.markdown( "<h3 style='text-align: left; color: red;'>Объем выборки (выборок) недостаточен для проверки гипотезы </h3>", unsafe_allow_html=True)
        else:
            if (len(data_male)>=3 and len(data_male)<20) or (len(data_female)>=3 and len(data_male)<20):
                st.write(':exclamation: Предупреждение: малый объем выборок может повлиять на корректность результата')
            ## Графики распределений
            tab1, tab2, tab3 =st.tabs(["Гистограмма",  "Распределение мужчины", "Распределение женщины"])
            with tab1:
                st.text("Распределение количества пропущенных рабочих дней по болезни для мужчин и женщин")
                chart_data = pd.DataFrame({"Мужчины": data_male.value_counts(), "Женщины": data_female.value_counts()})
                st.bar_chart(chart_data, use_container_width=True)

            with tab2:
                fig = go.Figure()
                fig.add_trace(go.Box(y=data_male, name='Мужчины'))
                fig.update_layout()
                st.plotly_chart(fig)

            with tab3:
                fig = go.Figure()
                fig.add_trace(go.Box(y=data_female, name='Женщины'))
                fig.update_layout()
                st.plotly_chart(fig)

            # проверка на нормальность выборок
            st.subheader('Проверка, являются ли выборки распределенными нормально')
            if shapiro(data_male, data_female):
                st.text("Для проверки гипотезы должна использоваться t-статистика, в разработке")
            else:
                # проверка гипотезы 1: мужчины пропускают в течение года более 2 рабочих дней по болезни значимо чаще женщин
                st.subheader('Проверка гипотезы')
                result=0
                # Результат проверки
                if mannwhitgreater(data_male, data_female, alpha):
                    st.markdown( "<h3 style='text-left: center; color: red;'>Гипотеза 1 подтверждена </h3>", unsafe_allow_html=True)
                else:
                    st.markdown( "<h3 style='text-left: center; color: red;'>Гипотеза 1 не подтверждена </h3>", unsafe_allow_html=True)
            
    
   
    if st.button('Проверить гипотезу 2'):
        result=0
        data_aged = df[df['age']>age]['sick_days'].sort_values()
        data_young = df[df['age']<=age]['sick_days'].sort_values()
        st.subheader('Выборки')
        st.text(f"Выборка 1: Сотрудники старше {age} лет, пропустившиее более {work_days} дней по болезни. \nOбъем выборки={len(data_aged)}")
        st.text (f"\nВыборка 2: Сотрудники {age} лет и младше, пропустившиее более {work_days} дней по болезни. \nOбъем выборки= {len(data_young)}")
        if (len(data_aged)<3 or len(data_young)<3):
            st.markdown( "<h3 style='text-align: left; color: red;'>Объем выборки (выборок) недостаточен для проверки гипотезы </h3>", unsafe_allow_html=True)
        else:
            if (len(data_aged)>=3 and len(data_aged)<20) or (len(data_young)>=3 and len(data_young)<20):
                st.text(":exclamation:Предупреждение: малый объем выборок может повлиять на корректность результата")
            ## Графики распределений
            tab1, tab2, tab3 =st.tabs(["Гистограмма",  "Распределение старше порога", "Распределение моложе порога"])

            with tab1:
                st.text("Распределение количества пропущенных рабочих дней среди сотрудников \nстарше и младше порога возраста")
                chart_data = pd.DataFrame({"Старше возрастного порога": data_aged.value_counts(), "Более молодые": data_young.value_counts()})
                st.bar_chart(chart_data, use_container_width=True)

            with tab2:
                fig = go.Figure()
                fig.add_trace(go.Box(y=data_aged, name='Cтарше возрастного порога'))
                fig.update_layout()
                st.plotly_chart(fig)

            with tab3:
                fig = go.Figure()
                fig.add_trace(go.Box(y=data_young, name='Более молодые сотрудники'))
                fig.update_layout()
                st.plotly_chart(fig)

            st.subheader('Проверка, являются ли выборки распределенными нормально')
            if shapiro(data_aged, data_young):
                st.text("Для проверки гипотезы должна использоваться t-статистика, в разработке")
            else:
                # проверка гипотезы 2: 
                st.subheader('Проверка гипотезы')
                if mannwhitgreater(data_aged, data_young, alpha):
                    st.markdown( "<h3 style='text-align: left; color: red;'>Гипотеза 2 подтверждена </h3>", unsafe_allow_html=True)
                else:
                    st.markdown( "<h3 style='text-align: left; color: red;'>Гипотеза 2 не подтверждена </h3>", unsafe_allow_html=True)

        