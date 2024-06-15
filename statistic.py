import sqlite3
import matplotlib.pyplot as plt

# Connect to SQLite database
db_file = 'image_optimization.db'
conn = sqlite3.connect(db_file)
c = conn.cursor()

# Fetch data from SQLite
c.execute('SELECT * FROM metrics')
row = c.fetchone()

if row:
    total_images_optimized = row[1]
    total_memory_saved = int(float(row[2][:-3]))
    total_time_saved = row[3]
    total_money_saved = row[4]

    # Prepare data for pie chart
    labels = ['Total Memory Saved', 'Total Time Saved', 'Total Money Saved']
    sizes = [total_memory_saved, total_time_saved, total_money_saved]

    # Plotting pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Optimization Metrics')
    plt.show()
else:
    print("No data found in the database.")

# Close SQLite connection
conn.close()
