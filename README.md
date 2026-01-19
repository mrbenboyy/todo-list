# Pokemon-Style Todo List App 🎮

A pixelated task manager with Pokemon-style graphics where you can create categories/goals and manage tasks within them!

## Features ✨

- **Categories/Goals**: Create different categories to organize your tasks
- **Task Management**: Add tasks to each category and mark them as done
- **Edit Functionality**: Edit category and task names with the "E" button
- **Pokemon-Style UI**: Authentic pixelated graphics with Pokemon-inspired colors
- **Pokemon Characters**: Pikachu mascot and Pokeball icons throughout
- **MongoDB Database**: All data is stored locally in MongoDB
- **Checkbox System**: Click anywhere on a task card or checkbox to toggle completion
- **Delete Options**: Remove categories or individual tasks with X buttons
- **Task Progress**: See completion status (e.g., "3/5 tasks") for each category

## Quick Start - Run the EXE 🚀

### For End Users (Just Run It!)

1. **Download** or build `PokemonTodo.exe`
2. **Make sure MongoDB is running** (see MongoDB setup below)
3. **Double-click** `PokemonTodo.exe`
4. That's it! Start organizing your tasks!

**Note:** You can move the .exe file anywhere (Desktop, Programs folder, etc.) and it will work!

---

## Building Your Own EXE 📦

### Easy Method (Recommended)

1. **Double-click** `build_exe.bat` in the project folder
2. Wait for the build to complete
3. Find your executable in the `dist` folder
4. Copy `PokemonTodo.exe` anywhere you want!

### Manual Method

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller PokemonTodo.spec

# Or use the full command:
pyinstaller --onefile --windowed --name="PokemonTodo" --add-data="PressStart2P-Regular.ttf;." --add-data="sprites;sprites" --noconsole main.py
```

Your executable will be in the `dist/` folder!

---

## MongoDB Setup 💾

The app requires MongoDB to store your todos. You only need to install it once!

### Install MongoDB (One-time setup)

**Windows:**
1. Download [MongoDB Community Edition](https://www.mongodb.com/try/download/community)
2. Run the installer (check "Install as Windows Service")
3. MongoDB will start automatically on boot!

**Alternative - MongoDB Compass:**
- If you installed MongoDB Compass, just open it
- MongoDB will start automatically

### Check if MongoDB is Running

Open Command Prompt and run:
```bash
mongosh
```
If you see a MongoDB shell, you're good to go!

### Start MongoDB Manually (if needed)

```bash
# Windows (if not running as service)
net start MongoDB

# Or run manually
mongod --dbpath C:\data\db
```

---

## For Developers 👨‍💻

### Prerequisites

1. **Python 3.7+** installed
2. **MongoDB** running locally at `mongodb://localhost:27017/`

### Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure MongoDB is running

4. Run the app:
```bash
python main.py
```

---

## How to Use 🎮

### Main Screen (Categories View):
- **View Categories**: See all your goal categories
- **Add Category**: Type in the input box at the bottom and click "+ Add"
- **Open Category**: Click on any category card to view its tasks
- **Delete Category**: Click the red "X" button (deletes category and all tasks)
- **Progress**: See how many tasks are completed in each category

### Tasks View:
- **Back Button**: Click "← Back" to return to categories
- **Toggle Task**: Click on a task card or its checkbox to mark as done/undone
- **Add Task**: Type in the input box and click "+ Add"
- **Delete Task**: Click the red "X" button to remove a task
- **Visual Feedback**: Completed tasks show with a green checkmark and light green background

## Controls ⌨️

- **Mouse**: Click to interact with all elements
- **Keyboard**: Type in input boxes
- **Enter**: Submit text when an input box is active
- **Backspace**: Delete text in input boxes

## Color Scheme 🎨

The app uses classic Pokemon colors:
- **Background**: Cream (#F0F0D0)
- **Yellow**: Pokemon yellow (#FFCB05)
- **Blue**: Pokemon blue (#3B86EA)
- **Green**: Success/completion (#78C850)
- **Red**: Delete buttons (#EA5455)

## Database Structure 💾

The app creates two collections in MongoDB:

**categories:**
```json
{
  "_id": ObjectId,
  "name": "My Goals",
  "created_at": ISODate
}
```

**tasks:**
```json
{
  "_id": ObjectId,
  "category_id": ObjectId,
  "name": "Complete this task",
  "completed": false,
  "created_at": ISODate
}
```

## Troubleshooting 🔧

**"Failed to connect to MongoDB"**
- Make sure MongoDB is installed and running
- Check if MongoDB is accessible at `mongodb://localhost:27017/`
- Try running: `mongod` in a terminal

**"pygame not found"**
- Install requirements: `pip install -r requirements.txt`

**App window is too small/large**
- Edit `SCREEN_WIDTH` and `SCREEN_HEIGHT` in `main.py` (default: 800x600)

## Tips 💡

- Keep category names short for best display (under 30 characters)
- You can have up to 8 categories visible at once
- Each category can show up to 8 tasks at once
- Completed tasks turn light green with a checkmark
- All data persists in MongoDB between sessions

## Future Enhancements 🚀

Potential features to add:
- Scrolling for more than 8 items
- Pokeball cursor or custom sprites
- Sound effects (Pokemon style!)
- Task priorities or due dates
- Export/import categories
- Dark mode toggle
- Custom color themes

Enjoy your Pokemon-style todo list! Gotta catch 'em all! ⚡
