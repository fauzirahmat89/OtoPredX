from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)

# Load the model
loaded_model = joblib.load('xgboost_regression_model.pkl')

# Fungsi untuk memformat harga dengan titik setiap tiga digit
def format_with_commas(price):
    price_str = '{:,.0f}'.format(price)
    return price_str

# Route to the homepage

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Ambil nilai input dari form
        year = int(request.form['Year'])
        kilometers_driven = int(request.form['Kilometers_Driven'])
        fuel_type = request.form['Fuel_Type']
        transmission = request.form['Transmission']
        mileage = float(request.form['Mileage'])
        engine = float(request.form['Engine'])
        power = float(request.form['Power'])
        seats = float(request.form['Seats'])

        # Buat DataFrame dengan nilai input
        data_input = pd.DataFrame({
            'Year': [year],
            'Kilometers_Driven': [kilometers_driven],
            'Fuel_Type': [fuel_type],
            'Transmission': [transmission],
            'Mileage': [mileage],
            'Engine': [engine],
            'Power': [power],
            'Seats': [seats]
        })

        # Prediksi harga mobil
        predicted_price = loaded_model.predict(data_input)

        # Konversi harga ke dalam IDR
        predicted_price_idr = int(predicted_price * 100 * 200000)
        lower = int(predicted_price_idr * 0.9)
        upper = int(predicted_price_idr * 1.1)

        # Format harga dengan titik setiap tiga digit
        predicted_price_formatted = format_with_commas(predicted_price_idr)
        predicted_lower_formatted = format_with_commas(lower)
        predicted_upper_formatted = format_with_commas(upper)
        

        # Render template dengan harga mobil yang diprediksi
        return render_template('index.html', predicted_price=predicted_price_formatted, predicted_lower = predicted_lower_formatted, predicted_upper = predicted_upper_formatted)

    # Render template dengan form input
    return render_template('index.html')

def read_csv(file_path):
    return pd.read_csv(file_path)

@app.route('/filter', methods=['POST'])
def filter_data():
    file_path = 'df_newData.csv'
    df = read_csv(file_path)
    column_name = request.form['column']
    filter_value_input = float(request.form['value'])  # Nilai input dari form
    priority_feature = request.form['priorityFeature']  # Priority feature from form

    # Initialize priority_value as None
    priority_value = None

    # Safely get the priority feature value from the form
    if priority_feature == 'Year':
        priority_value = request.form.get('priorityYear')
        if priority_value:
            priority_value = int(priority_value)
    elif priority_feature == 'Kilometers_Driven':
        priority_value = request.form.get('priorityKilometers')
        if priority_value:
            priority_value = int(priority_value)
    elif priority_feature == 'Engine':
        priority_value = request.form.get('priorityEngine')
        if priority_value:
            priority_value = int(priority_value)

    # Konversi nilai input menjadi mata uang Rupiah India (INR)
    filter_value = filter_value_input * 0.00000005

    # Urutkan DataFrame berdasarkan harga
    df_sorted = df.sort_values(by='Price')

    # Jika hasilnya kurang dari 0.01, tampilkan 5 data dengan harga terendah
    if filter_value < 0.01:
        filtered_df = df_sorted.head(5)
    else:
        # Cari 10 data dengan harga yang mendekati input pengguna
        filtered_df = df_sorted.iloc[(df_sorted['Price'] - filter_value).abs().argsort()[:10]]

    # Mengalikan kolom 'Price' dalam DataFrame dengan 100, lalu dengan 200.000
    if column_name == 'Price':
        filtered_df['Price'] = (filtered_df['Price'] * 100 * 200000).astype(int)

    # Filter the DataFrame based on the selected priority feature
    if priority_feature == 'Year' and priority_value is not None:
        filtered_df = filtered_df[filtered_df['Year'] >= priority_value]
    elif priority_feature == 'Kilometers_Driven' and priority_value is not None:
        filtered_df = filtered_df[filtered_df['Kilometers_Driven'] <= priority_value]
    elif priority_feature == 'Engine' and priority_value is not None:
        filtered_df = filtered_df[filtered_df['Engine'] >= priority_value]

    # Sort the filtered DataFrame based on the selected priority feature
    if priority_feature == 'Year':
        filtered_df = filtered_df.sort_values(by='Year', ascending=False)
    elif priority_feature == 'Kilometers_Driven':
        filtered_df = filtered_df.sort_values(by='Kilometers_Driven', ascending=True)
    elif priority_feature == 'Engine':
        filtered_df = filtered_df.sort_values(by='Engine', ascending=False)

    headers = df.columns
    data = filtered_df.values.tolist()
    return render_template('index.html', headers=headers, data=data)

if __name__ == '__main__':
    app.run(debug=True)