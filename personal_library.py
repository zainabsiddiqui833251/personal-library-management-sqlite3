import streamlit as st
import sqlite3
import pandas as pd

# Print SQLite version
conn = sqlite3.connect("library.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("SELECT sqlite_version();")
st.sidebar.info(f"SQLite Version: {cursor.fetchone()[0]}")

# Create Table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        title TEXT PRIMARY KEY,
        author TEXT,
        year INTEGER,
        genre TEXT,
        read_status BOOLEAN,
        rating INTEGER,
        summary TEXT
    )
""")
conn.commit()

st.sidebar.title("📚 Personal Library Manager")
menu = ["Add Book", "Remove Book", "Search Book", "View All Books", "Export Library"]
choice = st.sidebar.radio("Menu", menu)

# Function to fetch all books
def get_books():
    cursor.execute("SELECT * FROM books")
    return cursor.fetchall()

# Add Book
if choice == "Add Book":
    st.header("➕ Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=0, step=1)
        genre = st.text_input("Genre")
        read_status = st.checkbox("Have you read this book?")
        rating = st.slider("Rate the book", 1, 5, 3)
        summary = st.text_area("Write a short summary")
        submit = st.form_submit_button("Add Book")

        if submit:
            try:
                cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)", 
                               (title, author, year, genre, read_status, rating, summary))
                conn.commit()
                st.success(f"📖 '{title}' added successfully!")
            except sqlite3.IntegrityError:
                st.error("Book with this title already exists!")

# Remove Book
elif choice == "Remove Book":
    st.header("🗑 Remove a Book")
    books = get_books()
    book_titles = [book[0] for book in books] if books else []
    
    if book_titles:
        book_to_remove = st.selectbox("Select a book to remove", book_titles)
        if st.button("Remove Book"):
            cursor.execute("DELETE FROM books WHERE title = ?", (book_to_remove,))
            conn.commit()
            st.success(f"❌ '{book_to_remove}' removed successfully!")
    else:
        st.info("No books available to remove.")

# Search Book
elif choice == "Search Book":
    st.header("🔍 Search for a Book")
    search_term = st.text_input("Enter book title or author name to search")

    if search_term:
        cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", 
                       ('%' + search_term + '%', '%' + search_term + '%'))
        results = cursor.fetchall()

        if results:
            for book in results:
                st.markdown(f"**{book[0]}** by {book[1]} ({book[2]}) - {book[3]} - {'Read' if book[4] else 'Unread'} - ⭐ {book[5]}/5")
                st.text(f"Summary: {book[6]}")
        else:
            st.warning("No books found with that title or author.")

# View All Books
if choice == "View All Books":
    st.header("📚 Your Library")
    books = get_books()

    if books:
        df = pd.DataFrame(books, columns=["Title", "Author", "Year", "Genre", "Read", "Rating", "Summary"])
        st.dataframe(df)  # Display table
    else:
        st.info("Your library is empty. Add some books!")

# Export Library
elif choice == "Export Library":
    st.header("📤 Export Library")
    books = get_books()
    
    if books:
        df = pd.DataFrame(books, columns=["Title", "Author", "Year", "Genre", "Read", "Rating", "Summary"])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv, file_name="library.csv", mime="text/csv")
    else:
        st.info("No books available to export.")

# Close connection
conn.close()
