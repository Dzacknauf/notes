import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

# Nama file database
DB_NAME = "notes.db"

# Fungsi untuk membuat atau menginisialisasi database
def initialize_database():
    print("Inisialisasi database...")
    try:
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        connection.close()
        print("Database berhasil diinisialisasi.")
    except Exception as e:
        print(f"Error inisialisasi database: {e}")

# Aplikasi utama
class NotesApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inisialisasi database saat aplikasi dijalankan
        initialize_database()

    def build(self):
        """Membangun antarmuka utama aplikasi."""
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Input field untuk menambahkan catatan
        self.input_field = TextInput(
            hint_text="Tulis catatan di sini...",
            size_hint=(1, 0.1),
            multiline=False
        )
        self.layout.add_widget(self.input_field)

        # Tombol untuk menambahkan catatan
        add_button = Button(text="Tambah Catatan", size_hint=(1, 0.1))
        add_button.bind(on_press=self.add_note)
        self.layout.add_widget(add_button)

        # ScrollView untuk menampilkan daftar catatan
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.notes_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))
        self.scroll_view.add_widget(self.notes_layout)
        self.layout.add_widget(self.scroll_view)

        # Memuat catatan dari database saat aplikasi dimulai
        self.load_notes()

        return self.layout

    def load_notes(self):
        """Memuat semua catatan dari database ke antarmuka pengguna."""
        print("Memuat catatan dari database...")
        self.notes_layout.clear_widgets()
        notes = self.fetch_notes()
        for note_id, content in notes:
            self.create_note_widget(note_id, content)

    def fetch_notes(self):
        """Mengambil semua catatan dari database."""
        try:
            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()
            cursor.execute("SELECT id, content FROM notes ORDER BY date_created DESC")
            notes = cursor.fetchall()
            connection.close()
            return notes
        except Exception as e:
            print(f"Error fetching notes: {e}")
            return []

    def add_note_to_db(self, content):
        """Menambahkan catatan baru ke database."""
        try:
            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            connection.commit()
            connection.close()
            print("Catatan berhasil ditambahkan ke database.")
        except Exception as e:
            print(f"Error adding note to database: {e}")

    def delete_note_from_db(self, note_id):
        """Menghapus catatan dari database berdasarkan ID."""
        try:
            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            connection.commit()
            connection.close()
            print(f"Catatan dengan ID {note_id} berhasil dihapus.")
        except Exception as e:
            print(f"Error deleting note from database: {e}")

    def create_note_widget(self, note_id, content):
        """Membuat widget untuk satu catatan."""
        note_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        # Label untuk menampilkan teks catatan
        note_label = Label(
            text=content,
            size_hint_x=0.8,
            halign="left",
            valign="middle"
        )
        note_label.bind(size=note_label.setter('text_size'))  # Untuk multiline support
        note_box.add_widget(note_label)

        # Tombol untuk menghapus catatan
        delete_button = Button(text="Hapus", size_hint_x=0.2)
        delete_button.bind(on_press=lambda instance: self.delete_note(note_id))
        note_box.add_widget(delete_button)

        self.notes_layout.add_widget(note_box)

    def add_note(self, instance):
        """Menambahkan catatan baru dari input field."""
        content = self.input_field.text.strip()
        if content:  # Hanya tambahkan catatan jika tidak kosong
            print(f"Adding note: {content}")
            self.add_note_to_db(content)
            self.input_field.text = ""  # Kosongkan input field
            self.load_notes()
        else:
            print("Input field is empty.")

    def delete_note(self, note_id):
        """Menghapus catatan dan memperbarui tampilan."""
        print(f"Deleting note with ID: {note_id}")
        self.delete_note_from_db(note_id)
        self.load_notes()

if __name__ == '__main__':
    NotesApp().run()
