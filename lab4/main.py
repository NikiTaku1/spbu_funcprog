import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from recommender import get_recommendations, process_preferences

class BookRecommenderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Book Recommender")

        self.create_widgets()

    def create_widgets(self):
        # Preferences Input
        tk.Label(self.master, text="Favorite Genres (comma-separated):").grid(row=0, column=0, sticky="w")
        self.genres_entry = tk.Entry(self.master)
        self.genres_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(self.master, text="Favorite Authors (comma-separated):").grid(row=1, column=0, sticky="w")
        self.authors_entry = tk.Entry(self.master)
        self.authors_entry.grid(row=1, column=1, sticky="ew")

        tk.Label(self.master, text="Keywords (comma-separated):").grid(row=2, column=0, sticky="w")
        self.keywords_entry = tk.Entry(self.master)
        self.keywords_entry.grid(row=2, column=1, sticky="ew")

        tk.Label(self.master, text="Minimum Publication Year (optional):").grid(row=3, column=0, sticky="w")
        self.year_entry = tk.Entry(self.master)
        self.year_entry.grid(row=3, column=1, sticky="ew")

        # Sorting Options
        tk.Label(self.master, text="Sort By:").grid(row=4, column=0, sticky="w")
        self.sort_options = ["Rating", "Year", "Name"]
        self.sort_var = tk.StringVar(value="Rating") #Default sort
        self.sort_menu = ttk.Combobox(self.master, textvariable=self.sort_var, values=self.sort_options)
        self.sort_menu.grid(row=4, column=1, sticky="ew")


        # Get Recommendations Button
        self.get_recs_button = tk.Button(self.master, text="Get Recommendations", command=self.get_recommendations)
        self.get_recs_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Recommendations Display
        self.recommendations_text = tk.Text(self.master, wrap=tk.WORD, height=10)
        self.recommendations_text.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.recommendations_text.config(state=tk.DISABLED)

        self.save_button = tk.Button(self.master, text="Save Selected Recommendations", command=self.save_selected_recommendations)
        self.save_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Configure column weights
        self.master.columnconfigure(1, weight=1)


    def get_recommendations(self):
        try:
            genres = self.genres_entry.get().split(",")
            authors = self.authors_entry.get().split(",")
            keywords = self.keywords_entry.get().split(",")
            year_str = self.year_entry.get()
            year_filter = int(year_str) if year_str else None
            sort_by = self.sort_var.get()

            preferences = process_preferences(genres, authors, keywords)
            recommendations = get_recommendations(preferences, year_filter=year_filter, sort_by=sort_by)

            self.recommendations_text.config(state=tk.NORMAL)
            self.recommendations_text.delete("1.0", tk.END)

            if recommendations:
                self.recommendations = [] #Store recommendations for saving later.
                for i, (book, score) in enumerate(recommendations):
                    self.recommendations.append((book, score)) #Append to list
                    self.recommendations_text.insert(tk.END, f"{i+1}. Title: {book['title']}, Author: {', '.join(book['author'])}, Score: {score}\n")
            else:
                self.recommendations_text.insert(tk.END, "No recommendations found.")

            self.recommendations_text.config(state=tk.DISABLED)

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid data.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def save_selected_recommendations(self):
        if not self.recommendations:
            messagebox.showwarning("Warning", "No recommendations to save.")
            return

        try:
            indices_str = tk.simpledialog.askstring("Save Selection", "Enter indices to save (comma-separated, e.g., 1,3,5):")
            if indices_str:
                indices = [int(x.strip()) for x in indices_str.split(',') if x.strip()]
                
                if not all(1 <= i <= len(self.recommendations) for i in indices):
                    raise ValueError("Invalid indices. Please enter numbers within the valid range.")
                    
                recommendations_to_save = [self.recommendations[i-1] for i in indices]
                
                filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
                if filepath:
                    data_to_save = [{"title": book["title"], "author": book["author"], "genre": book["genre"], "year": book["first_publish_year"], "score": score} for book, score in recommendations_to_save]
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data_to_save, f, indent=4)
                    messagebox.showinfo("Success", f"Recommendations saved to {filepath}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error saving to JSON: {e}")



root = tk.Tk()
gui = BookRecommenderGUI(root)
root.mainloop()