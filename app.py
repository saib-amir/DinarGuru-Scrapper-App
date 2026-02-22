import customtkinter as ctk
from tkinter import messagebox
import threading

from dinar_guru_bot import run_dinar_guru_bot
from dinar_recaps_bot import run_dinar_recaps_bot
from word_press_bot import run_wordpress_bot
from utils import download_json, download_csv


class DinarGuruApp(ctk.CTk):
    """Main application window for Dinar bot interface."""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Dinar Bot")
        self.attributes("-zoomed", True)

        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Shared variable to store posts
        self.posts: list[dict] = []

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=0)
        self.grid_rowconfigure(3, weight=1)  # Posts area expands

        # Create UI components
        self._create_bot_section()
        self._create_status_label()
        self._create_posts_display()

    def _create_bot_section(self):
        """Create the Bots section with bot buttons."""
        # Bots heading
        bots_heading = ctk.CTkLabel(
            self,
            text="Post Bots",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        bots_heading.grid(row=0, column=0, pady=(20, 10))

        # Bot buttons frame
        bot_frame = ctk.CTkFrame(self, fg_color="transparent")
        bot_frame.grid(row=1, column=0, pady=(10, 5), padx=40, sticky="ew")
        bot_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="buttons")

        # DinarGuru button
        self.btn_dinar_guru = ctk.CTkButton(
            bot_frame,
            text="DinarGuru",
            command=self._run_dinar_guru,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2d5a27",
            hover_color="#3d7a37",
        )
        self.btn_dinar_guru.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # DinarRecaps button
        self.btn_dinar_recaps = ctk.CTkButton(
            bot_frame,
            text="DinarRecaps",
            command=self._run_dinar_recaps,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4a4a8a",
            hover_color="#5a5a9a",
        )
        self.btn_dinar_recaps.grid(row=0, column=1, padx=10, sticky="ew")

        # DinarTiru button (placeholder)
        self.btn_dinar_tiru = ctk.CTkButton(
            bot_frame,
            text="DinarTiru",
            command=self._run_dinar_tiru,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8a4a4a",
            hover_color="#9a5a5a",
        )
        self.btn_dinar_tiru.grid(row=0, column=2, padx=(10, 0), sticky="ew")

    def _create_status_label(self):
        """Create a status label below the bot section."""
        # Status frame with background
        self.status_frame = ctk.CTkFrame(
            self,
            fg_color="#1a1a2e",
            corner_radius=8,
            height=50,
        )
        self.status_frame.grid(row=2, column=0, pady=(10, 20), padx=40, sticky="ew")
        self.status_frame.grid_propagate(False)
        self.status_frame.grid_rowconfigure(0, weight=1)

        # Inner frame to hold dot and label, centered in status_frame
        self.status_inner = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        self.status_inner.grid(row=0, column=0)
        self.status_frame.grid_columnconfigure(0, weight=1)

        # Status indicator dot
        self.status_dot = ctk.CTkLabel(
            self.status_inner,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color="#4ade80",
        )
        self.status_dot.grid(row=0, column=0, padx=(0, 8))

        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_inner,
            text="Ready",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e0e0e0",
        )
        self.status_label.grid(row=0, column=1)

    def _create_posts_display(self):
        """Create a scrollable area to display extracted posts with download dropdown."""
        # Posts section container
        self.posts_section = ctk.CTkFrame(self, fg_color="transparent")
        self.posts_section.grid(row=3, column=0, pady=(10, 20), padx=40, sticky="nsew")
        self.posts_section.grid_columnconfigure(0, weight=1)
        self.posts_section.grid_rowconfigure(1, weight=1)

        # Header frame with title and download dropdown
        header_frame = ctk.CTkFrame(self.posts_section, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Posts heading (left side)
        posts_heading = ctk.CTkLabel(
            header_frame,
            text="Extracted Posts",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        posts_heading.grid(row=0, column=0, sticky="w")

        # Actions frame (right side) - contains WP Publish and Download buttons
        self.actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.actions_frame.grid(row=0, column=1, sticky="e")
        self.actions_frame.grid_remove()  # Hidden initially

        # WP Publish button
        self.btn_wp_publish = ctk.CTkButton(
            self.actions_frame,
            text="Publish to WP",
            command=self._run_wordpress_publish,
            width=130,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#16a34a",
            hover_color="#15803d",
        )
        self.btn_wp_publish.grid(row=0, column=0, padx=(0, 10))

        # Download dropdown frame
        self.download_dropdown_frame = ctk.CTkFrame(
            self.actions_frame, fg_color="transparent"
        )
        self.download_dropdown_frame.grid(row=0, column=1, sticky="e")

        # Download button that toggles dropdown
        self.btn_download = ctk.CTkButton(
            self.download_dropdown_frame,
            text="Download ▼",
            command=self._toggle_download_menu,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        self.btn_download.grid(row=0, column=0)

        # Dropdown menu frame (hidden by default)
        self.download_menu = ctk.CTkFrame(
            self.download_dropdown_frame,
            fg_color="#1e1e2e",
            corner_radius=8,
        )
        self.download_menu.grid(row=1, column=0, sticky="e", pady=(5, 0))
        self.download_menu.grid_remove()  # Hidden initially

        # JSON option button
        self.btn_json = ctk.CTkButton(
            self.download_menu,
            text="JSON",
            command=self._download_json,
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#374151",
            anchor="w",
        )
        self.btn_json.grid(row=0, column=0, padx=5, pady=(5, 2))

        # CSV option button
        self.btn_csv = ctk.CTkButton(
            self.download_menu,
            text="CSV",
            command=self._download_csv,
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#374151",
            anchor="w",
        )
        self.btn_csv.grid(row=1, column=0, padx=5, pady=(2, 5))

        # Scrollable frame for posts
        self.posts_frame = ctk.CTkScrollableFrame(
            self.posts_section,
            fg_color="transparent",
            corner_radius=10,
        )
        self.posts_frame.grid(row=1, column=0, sticky="nsew")
        self.posts_frame.grid_columnconfigure(0, weight=1)

        # Placeholder label when no posts
        self.no_posts_label = ctk.CTkLabel(
            self.posts_frame,
            text="No posts extracted yet. Run a bot to see posts here.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.no_posts_label.grid(row=0, column=0, pady=20)

    def _toggle_download_menu(self):
        """Toggle the download dropdown menu visibility."""
        if self.download_menu.winfo_viewable():
            self.download_menu.grid_remove()
            self.btn_download.configure(text="Download ▼")
        else:
            self.download_menu.grid()
            self.btn_download.configure(text="Download ▲")

    def _update_posts_display(self):
        """Update the posts display with current posts."""
        # Clear existing widgets in posts frame
        for widget in self.posts_frame.winfo_children():
            widget.destroy()

        # Hide dropdown menu if open
        self.download_menu.grid_remove()
        self.btn_download.configure(text="Download ▼")

        if not self.posts:
            # Hide actions frame when no posts
            self.actions_frame.grid_remove()
            self.no_posts_label = ctk.CTkLabel(
                self.posts_frame,
                text="No posts extracted yet. Run a bot to see posts here.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            )
            self.no_posts_label.grid(row=0, column=0, pady=20)
            return

        # Show actions frame when posts exist
        self.actions_frame.grid()

        # Display each post with date and title
        for i, post in enumerate(self.posts):
            post_frame = ctk.CTkFrame(
                self.posts_frame, fg_color="#2b2b2b", corner_radius=8
            )
            post_frame.grid(row=i, column=0, pady=5, padx=10, sticky="ew")
            post_frame.grid_columnconfigure(1, weight=1)

            # Date label
            date_text = post.get("date", "No date")
            date_label = ctk.CTkLabel(
                post_frame,
                text=date_text,
                font=ctk.CTkFont(size=12),
                text_color="#888888",
                width=120,
                anchor="w",
            )
            date_label.grid(row=0, column=0, padx=(15, 10), pady=10, sticky="w")

            # Title label
            title_text = post.get("title", "No title")
            title_label = ctk.CTkLabel(
                post_frame,
                text=title_text,
                font=ctk.CTkFont(size=14),
                anchor="w",
            )
            title_label.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="w")

    def _set_status(self, message: str, status_type: str = "info"):
        """Update the status label with appropriate styling.

        Args:
            message: The status message to display
            status_type: One of 'info', 'success', 'error', 'working'
        """
        self.status_label.configure(text=message)

        # Update dot color based on status type
        dot_colors = {
            "info": "#4ade80",  # Green - ready/info
            "success": "#4ade80",  # Green - success
            "error": "#f87171",  # Red - error
            "working": "#fbbf24",  # Yellow/amber - in progress
        }
        self.status_dot.configure(text_color=dot_colors.get(status_type, "#4ade80"))
        self.update()

    def _set_buttons_state(self, state: str):
        """Enable or disable bot buttons."""
        buttons = [
            self.btn_dinar_guru,
            self.btn_dinar_recaps,
            self.btn_dinar_tiru,
        ]
        for btn in buttons:
            btn.configure(state=state)

    def _run_dinar_guru(self):
        """Run the DinarGuru bot to extract posts."""
        self._set_buttons_state("disabled")
        self._set_status("Extracting posts from DinarGuru...", "working")

        def extract_thread():
            try:
                self.posts = run_dinar_guru_bot()
                self.after(0, lambda: self._on_extraction_complete(len(self.posts)))
            except Exception as e:
                self.after(0, lambda: self._on_extraction_error(str(e)))

        thread = threading.Thread(target=extract_thread, daemon=True)
        thread.start()

    def _on_extraction_complete(self, count: int):
        """Handle successful extraction."""
        self._set_buttons_state("normal")
        self._set_status(f"Extracted {count} posts successfully!", "success")
        self._update_posts_display()
        messagebox.showinfo("Success", f"Extracted {count} posts from DinarGuru!")

    def _on_extraction_error(self, error: str):
        """Handle extraction error."""
        self._set_buttons_state("normal")
        self._set_status("Error extracting posts", "error")
        messagebox.showerror("Error", f"Failed to extract posts:\n{error}")

    def _run_dinar_recaps(self):
        """Run the DinarRecaps bot to extract posts."""
        self._set_buttons_state("disabled")
        self._set_status("Extracting posts from DinarRecaps...", "working")

        def extract_thread():
            try:
                self.posts = run_dinar_recaps_bot()
                self.after(
                    0, lambda: self._on_recaps_extraction_complete(len(self.posts))
                )
            except Exception as e:
                self.after(0, lambda: self._on_recaps_extraction_error(str(e)))

        thread = threading.Thread(target=extract_thread, daemon=True)
        thread.start()

    def _on_recaps_extraction_complete(self, count: int):
        """Handle successful DinarRecaps extraction."""
        self._set_buttons_state("normal")
        self._set_status(f"Extracted {count} posts successfully!", "success")
        self._update_posts_display()
        messagebox.showinfo("Success", f"Extracted {count} posts from DinarRecaps!")

    def _on_recaps_extraction_error(self, error: str):
        """Handle DinarRecaps extraction error."""
        self._set_buttons_state("normal")
        self._set_status("Error extracting posts", "error")
        messagebox.showerror("Error", f"Failed to extract posts:\n{error}")

    def _run_dinar_tiru(self):
        """Placeholder for DinarTiru bot."""
        messagebox.showinfo("Info", "DinarTiru bot not yet implemented.")

    def _run_wordpress_publish(self):
        """Run the WordPress bot to publish extracted posts."""
        if not self.posts:
            messagebox.showwarning(
                "Warning", "No posts to publish. Extract posts first!"
            )
            return

        # Confirm before publishing
        post_count = len(self.posts)
        confirm = messagebox.askyesno(
            "Confirm Publish",
            f"Are you sure you want to publish {post_count} posts to WordPress?\n\n"
            "This will open a browser window. You may need to log in manually.",
        )

        if not confirm:
            return

        self._set_buttons_state("disabled")
        self.btn_wp_publish.configure(state="disabled")
        self._set_status("Publishing posts to WordPress...", "working")

        def publish_thread():
            try:
                published_count = run_wordpress_bot(self.posts)
                self.after(0, lambda: self._on_wp_publish_complete(published_count))
            except Exception as e:
                self.after(0, lambda: self._on_wp_publish_error(str(e)))

        thread = threading.Thread(target=publish_thread, daemon=True)
        thread.start()

    def _on_wp_publish_complete(self, count: int):
        """Handle successful WordPress publishing."""
        self._set_buttons_state("normal")
        self.btn_wp_publish.configure(state="normal")
        self._set_status(f"Published {count} posts to WordPress!", "success")
        messagebox.showinfo(
            "Success", f"Successfully published {count}/{len(self.posts)} posts to WordPress!"
        )

    def _on_wp_publish_error(self, error: str):
        """Handle WordPress publishing error."""
        self._set_buttons_state("normal")
        self.btn_wp_publish.configure(state="normal")
        self._set_status("Error publishing to WordPress", "error")
        messagebox.showerror("Error", f"Failed to publish posts:\n{error}")

    def _download_json(self):
        """Download posts as JSON file."""
        # Close dropdown menu
        self.download_menu.grid_remove()
        self.btn_download.configure(text="Download ▼")

        if not self.posts:
            messagebox.showwarning("Warning", "No posts to download. Run a bot first!")
            return

        try:
            file_path = download_json(self.posts)
            self._set_status(f"Saved to {file_path}", "success")
            messagebox.showinfo("Success", f"JSON file saved to:\n{file_path}")
        except Exception as e:
            self._set_status("Failed to save file", "error")
            messagebox.showerror("Error", f"Failed to save JSON:\n{e}")

    def _download_csv(self):
        """Download posts as CSV file."""
        # Close dropdown menu
        self.download_menu.grid_remove()
        self.btn_download.configure(text="Download ▼")

        if not self.posts:
            messagebox.showwarning("Warning", "No posts to download. Run a bot first!")
            return

        try:
            file_path = download_csv(self.posts)
            self._set_status(f"Saved to {file_path}", "success")
            messagebox.showinfo("Success", f"CSV file saved to:\n{file_path}")
        except Exception as e:
            self._set_status("Failed to save file", "error")
            messagebox.showerror("Error", f"Failed to save CSV:\n{e}")


def main():
    """Entry point for the application."""
    app = DinarGuruApp()
    app.mainloop()


if __name__ == "__main__":
    main()
