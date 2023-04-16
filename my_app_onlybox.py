import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import random
from wordcloud import WordCloud
import pandas as pd
import panel as pn
import param
import altair as alt
import seaborn as sns



data = pd.read_excel('Refined_IT-Salary-Survey-EU-2020-csv (1).xls')

print(data.columns)

data.describe()

data = data[data['Gender'] != 'Diverse']

data = data[data['Yearly brutto salary (without bonus and stocks) in EUR'] <= 500000]

data = data[data['Сontract duration'] != '0']

import pandas as pd

# Define a mapping dictionary
mapping = {'Full-time employee': 'Full-time employee',
           'Self-employed (freelancer)': 'Other',
           'Part-time employee': 'Other',
           'Founder': 'Other',
           'Working Student': 'Other',
           'Company Director': 'Other',
           'Full-time position, part-time position, & self-employed (freelancing, tutoring)': 'Other',
           'Intern': 'Other',
           "full-time, but 32 hours per week (it was my request, I'm a student)": 'Other',
           'Werkstudent': 'Other'}

# Create a new column using the mapping dictionary
data['Employment_status_group'] = data['Employment status'].map(mapping)

# Check the value counts of the new column
print(data['Employment_status_group'].value_counts())

# Remove any leading/trailing whitespaces and make the values lowercase
data['Number of vacation days'] = data['Number of vacation days'].str.strip().str.lower()

# Replace the string values with numerical values
data['Number of vacation days'].replace({
    '(no idea)': 30,
    'unlimited': 30,
    '30 in contract (but theoretically unlimited)': 30,
    '~25': 25,
    '23+': 23,
    '24 labour days': 24
}, inplace=True)

# Drop rows with non-numerical values
data = data[pd.to_numeric(data['Number of vacation days'], errors='coerce').notna()]

data.loc[data['Number of vacation days'] == '37.5', 'Number of vacation days'] = 37

# Convert the column to numerical type
data['Number of vacation days'] = data['Number of vacation days'].astype(int)

data = data[data['Number of vacation days'] <= 30]

# Remove any leading/trailing whitespaces and make the values lowercase
data['Total years of experience'] = data['Total years of experience'].str.strip().str.lower()

# Replace the string values with numerical values
data['Total years of experience'].replace({
    '15, thereof 8 as CTO ': 15,
    '1 (as QA Engineer) / 11 in total ': 1,
    'less than year ': 1
}, inplace=True)

# Drop rows with non-numerical values
data = data[pd.to_numeric(data['Total years of experience'], errors='coerce').notna()]

data.loc[data['Total years of experience'] == '5.5', 'Total years of experience'] = 5
data.loc[data['Total years of experience'] == '2.5', 'Total years of experience'] = 2
data.loc[data['Total years of experience'] == '1,5', 'Total years of experience'] = 1
data.loc[data['Total years of experience'] == '1.5', 'Total years of experience'] = 1
data.loc[data['Total years of experience'] == '3.5', 'Total years of experience'] = 3
data.loc[data['Total years of experience'] == '4.5', 'Total years of experience'] = 4
data.loc[data['Total years of experience'] == '0.8', 'Total years of experience'] = 1
data.loc[data['Total years of experience'] == '2,5', 'Total years of experience'] = 2
data.loc[data['Total years of experience'] == '7.5', 'Total years of experience'] = 7
data.loc[data['Total years of experience'] == '6.5', 'Total years of experience'] = 6
data.loc[data['Total years of experience'] == '8.5', 'Total years of experience'] = 8



# Convert the column to numerical type
data['Total years of experience'] = data['Total years of experience'].astype(int)

data['Total years of experience'].value_counts()


"""# **2**"""

import pandas as pd
import altair as alt
import panel as pn
pn.extension('vega')

list(data.columns)

data.columns = list(data.columns)

def create_base_chart(data, x_value, y_value, color_value, tooltip_value):
    chart = alt.Chart(data).mark_boxplot().encode(
        x=x_value,
        y=y_value,
        color=color_value,
        tooltip=tooltip_value
    ).interactive()
    return chart

def create_filtered_chart(data, gender, company_size, age_range):
    job_positions = job_positions = ['Software Engineer','Backend Developer','Frontend Developer','QA Engineer', 'Data Scientist']
    data = data[data['Gender'].apply(lambda x: isinstance(x, str))]  # Keep rows with string values in the 'Gender' column
    filtered_data = data[
        (data['Gender'].str.lower().isin([str(g).lower() for g in gender])) &
        (data['Company size'].isin(company_size)) &
        (data['Position'].isin(job_positions)) &
        (data['Age'] >= age_range[0]) &
        (data['Age'] <= age_range[1])
    ]
    chart = create_base_chart(filtered_data, 'Position', 'Yearly brutto salary (without bonus and stocks) in EUR', 'Seniority level', ['Position', 'Yearly brutto salary (without bonus and stocks) in EUR', 'Company size', 'Gender', 'Age'])
    return chart

def create_pie_chart(data, column, gender):
    data = data[data['Gender'].str.lower() == gender.lower()]
    data = data.groupby(column).size().reset_index(name='counts')
    chart = alt.Chart(data).mark_arc(innerRadius=50, outerRadius=100, cornerRadius=5).encode(
        theta=alt.Theta('counts:Q', stack=True),
        color=alt.Color(f"{column}:N", scale=alt.Scale(scheme='category20')),
        tooltip=[column, 'counts']
    ).properties(width=200, height=200, title=f"{gender} Job Positions")
    return chart


def plot_word_cloud(data, column_name, image_path='wordcloud.png'):
    text = ' '.join(data[column_name].dropna().str.lower())
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis', max_words=100).generate(text)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

def create_violin_chart(data, x_value, y_value, hue_value, palette=None):
    plt.figure(figsize=(12, 6))
    sns.violinplot(x=x_value, y=y_value, data=data, hue=hue_value, split=True, inner="quartile", palette=palette)
    plt.title('Salary Distribution by Company Type')
    plt.legend(title=hue_value, loc='upper left')
    plt.tight_layout()
    plt.savefig('violin_chart.png', format='png', bbox_inches='tight')
    plt.close()


# Create position_widget after loading and cleaning the data
job_positions = ['Software Engineer', 'Backend Developer', 'Frontend Developer', 'QA Engineer', 'Data Scientist']

age_widget = pn.widgets.IntRangeSlider(name='Age Range', start=20, end=60, value=(25, 55), step=1)


position_checkbox = pn.widgets.CheckBoxGroup(name="Select Job Position", options=job_positions, value=job_positions)

seniority_checkbox = pn.widgets.CheckBoxGroup(name='Seniority', options=['Lead', 'Middle', 'Junior'], value=['Lead', 'Middle', 'Junior'])
company_size_checkbox = pn.widgets.CheckBoxGroup(name='Company Size', options=['51-100', '101-1000', '11-50', '1000+', 'up to 10'], value=['51-100', '101-1000', '11-50', '1000+', 'up to 10'])

@pn.depends(seniority_checkbox.param.value, company_size_checkbox.param.value, age_widget.param.value, position_checkbox.param.value)
def update_box_plot(seniority, company_size, age_range, selected_positions):



    filtered_data = data[
        (data['Seniority level'].isin(seniority)) &
        (data['Company size'].isin(company_size)) &
        (data['Position'].isin(selected_positions)) &
        (data['Age'] >= age_range[0]) &
        (data['Age'] <= age_range[1])
    ]

    # Filter data based on selected positions
    filtered_data = filtered_data[filtered_data['Position'].isin(selected_positions)]

    base = alt.Chart(filtered_data).encode(
        x=alt.X('Gender:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
        y=alt.Y('Yearly brutto salary (without bonus and stocks) in EUR:Q', title='Salary'),
        color=alt.Color('Gender:N', title=None, scale=alt.Scale(domain=['Male', 'Female'], range=['blue', 'pink'])),
        column=alt.Column('Position:N', title=None, header=alt.Header(labelAngle=0, labelOrient="bottom", labelAlign='center', labelPadding=15)),
    )

    box_plot = base.mark_boxplot(size=40).encode(
        tooltip=['Position', 'Gender', 'Yearly brutto salary (without bonus and stocks) in EUR']
    )

    pie_chart_male = create_pie_chart(filtered_data, 'Position', 'Male')
    pie_chart_female = create_pie_chart(filtered_data, 'Position', 'Female')

    # violin_chart = create_violin_chart(filtered_data, 'Company type', 'Yearly brutto salary (without bonus and stocks) in EUR', 'Company type', ['Company type', 'Yearly brutto salary (without bonus and stocks) in EUR'])


    return pn.Row(box_plot.properties(width=100, height=400), pie_chart_male, pie_chart_female)




# Create titles for each checkbox group
position_title = pn.pane.Markdown("#### Select Job Position")
seniority_title = pn.pane.Markdown("#### Seniority")
company_size_title = pn.pane.Markdown("#### Company Size")
age_title = pn.pane.Markdown("#### Age Range")

# Create the layout with titles and checkbox groups
widgets = pn.Column(
    pn.Row(pn.Column(position_title, position_checkbox)),
    pn.Row(pn.Column(seniority_title, seniority_checkbox)),
    pn.Row(pn.Column(company_size_title, company_size_checkbox)),
    pn.Row(pn.Column(age_title, age_widget))
)

plot_word_cloud(data, "Your main technology / programming language", 'wordcloud.png')
# Find the top 8 most populated company types
top_company_types = data['Company type'].value_counts().nlargest(6).index

# Filter the data to include only the top 8 company types
filtered_data_company = data[data['Company type'].isin(top_company_types)]
create_violin_chart(filtered_data_company, 'Company type', 'Yearly brutto salary (without bonus and stocks) in EUR', 'Gender', {'Male': 'blue', 'Female': 'pink'})




violin_chart_image = pn.pane.PNG('violin_chart.png', width=800, height=400)
wordcloud_image = pn.pane.PNG('wordcloud.png', width=800, height=400)
chart = pn.panel(pn.bind(update_box_plot, seniority=seniority_checkbox, company_size=company_size_checkbox, age_range=age_widget, selected_positions=position_checkbox))


# Create titles for each checkbox group
position_title = pn.pane.Markdown("#### Select Job Position")
seniority_title = pn.pane.Markdown("#### Seniority")
company_size_title = pn.pane.Markdown("#### Company Size")
age_title = pn.pane.Markdown("#### Age Range")

# Create the layout with titles and checkbox groups
widgets = pn.Column(
    pn.Row(pn.Column(position_title, position_checkbox)),
    pn.Row(pn.Column(seniority_title, seniority_checkbox)),
    pn.Row(pn.Column(company_size_title, company_size_checkbox)),
    pn.Row(pn.Column(age_title, age_widget))
)

# Description of the dataset, graphs, and the issue
# Description of the dataset, graphs, and the issue with HTML elements
description = pn.pane.Markdown("""
<h2 style="color: #4a4a4a; font-family: Arial, sans-serif;">IT Salary Survey Dashboard</h2>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    This dashboard is based on the IT Salary Survey data for Europe in 2020. <br> It focuses on the issue of male vs. female salaries in various positions and company types. The charts help visualize the salary distribution by gender, position, seniority, company size, and age.
</p>
<h3 style="color: #4a4a4a; font-family: Arial, sans-serif;">Main Elements</h3>
<ol style="color: #4a4a4a; font-family: Arial, sans-serif;">
    <li>An interactive box plot that shows the salary distribution by position, seniority, company size, and age.</li>
    <li>Pie charts displaying the distribution in jobs for males and females.</li>
    <li>A word cloud showing the main technologies and programming languages in the dataset.</li>
    <li>A violin chart illustrating the salary distribution for the top 6 most populated company types by gender.</li>
    <li>Bubble and Bar Charts showing the relationship between age, salary, and total years of experience for selected positions in the tech industry</li>
</ol>
""")

# Description of the box plot
box_plot_description = pn.pane.Markdown("""
<h3 style="color: #4a4a4a; font-family: Arial, sans-serif;">Box Plot</h3>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    This interactive box plot shows the salary distribution by position, seniority, company size, and age. You can filter the data by selecting different values in the widgets. The plot allows you to compare the salary distribution between male and female employees in various positions and seniority levels.
</p>
""")

# Description of the pie charts
pie_chart_description = pn.pane.Markdown("""
<h3 style="color: #4a4a4a; font-family: Arial, sans-serif;">Pie Charts</h3>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    These pie charts display the proportion of male and female job positions. The charts help visualize the gender balance in the selected positions across different company sizes and seniority levels.
</p>
<br><br>
""")

# Description of the word cloud
word_cloud_description = pn.pane.Markdown("""
<h3 style="color: #4a4a4a; font-family: Arial, sans-serif;">Word Cloud</h3>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    The word cloud shows the main technologies and programming languages in the dataset. The size of each word represents the frequency of its occurrence. It provides an overview of the most popular skills and languages in the IT industry.
</p>
""")

# Description of the violin chart
violin_chart_description = pn.pane.Markdown("""
<h3 style="color: #4a4a4a; font-family: Arial, sans-serif;">Violin Chart</h3>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    This violin chart illustrates the salary distribution for the top 6 most populated company types by gender. The chart allows you to compare the salary distribution between male and female employees across different company types.
</p>
""")


bubble_bar_chart_description = pn.pane.Markdown("""
<h3 style="color: #4a4a4a; font-family: Arial, sans-serif;">Bubble and Bar Charts</h3>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    These interactive charts show the relationship between age, salary, and total years of experience for selected positions in the tech industry. The bubble chart displays individual data points, where the size of each bubble represents the total years of experience. You can filter the data by selecting one or more positions on the bar chart, which displays the count of employees in each position.
</p>
<p style="color: #4a4a4a; font-family: Arial, sans-serif;">
    To explore the data further, you can use the interval selection tool on the bubble chart's x-axis to select a specific age range. This will filter the bar chart, showing only the count of employees within the selected age range.
</p>
""")


# Define the color scale
scale = alt.Scale(
    domain=[
        "Software Engineer",
        "Backend Developer",
        "Frontend Developer",
        "QA Engineer",
        "Data Scientist",
    ],
    range=["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
)
color = alt.Color("Position:N", scale=scale)

# Create multiple selection on the bar chart
click = alt.selection_multi(encodings=["color"])
# Create interval selection on the bubble chart
brush = alt.selection_interval(encodings=["x"])

# Create a bubble chart
points = (
    alt.Chart(data)
    .mark_point()
    .encode(
        alt.X("Age:Q", title="Age"),
        alt.Y(
            "Yearly brutto salary (without bonus and stocks) in EUR:Q",
            title="Salary",
            scale=alt.Scale(domain=[0, 200000]),
        ),
        color=color,
        size=alt.Size("Total years of experience:Q", scale=alt.Scale(range=[5, 200])),
    )
    .properties(width=800, height=300)
    .transform_filter(click)
    .add_selection(brush)
)

# Filter the data to include only the desired positions
filtered_data = data[
    data["Position"].isin(
        [
            "Software Engineer",
            "Backend Developer",
            "Frontend Developer",
            "QA Engineer",
            "Data Scientist",
        ]
    )
]

# Create a bar chart with filtered data
bars = (
    alt.Chart(filtered_data)
    .mark_bar()
    .encode(
        x="count()",
        y="Position:N",
        color=alt.condition(click, color, alt.value("lightgrey")),
    )
    .properties(width=800)
    .add_selection(click)
    .transform_filter(brush)
)

# Add the new charts to the layout
app = pn.Column(
    description,
    box_plot_description,
    pie_chart_description,
    pn.Row(widgets, chart),
    word_cloud_description,
    wordcloud_image,
    violin_chart_description,
    violin_chart_image,
    bubble_bar_chart_description,
    points & bars
)

app.servable()

app.show()
