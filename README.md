# Pokemon-Style Todo List App 🎮

A pixelated task manager with Pokemon-style graphics where you can create categories/goals and manage tasks within them!

## Features ✨

- **Categories/Goals**: Create different categories to organize your tasks
- **Task Management**: Add tasks to each category and mark them as done
- **Pokemon-Style UI**: Pixelated graphics with Pokemon-inspired colors
- **MongoDB Database**: All data is stored locally in MongoDB
- **Checkbox System**: Click anywhere on a task card or checkbox to toggle completion
- **Delete Options**: Remove categories or individual tasks with X buttons
- **Task Progress**: See completion status (e.g., "3/5 tasks") for each category

## Prerequisites 📋

1. **Python 3.7+** installed on your system
2. **MongoDB** running locally at `mongodb://localhost:27017/`

### Installing MongoDB

**Windows:**
1. Download from [MongoDB Community Edition](https://www.mongodb.com/try/download/community)
2. Install and run MongoDB as a service
3. Or run manually: `mongod --dbpath C:\data\db`

## Installation 🚀

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure MongoDB is running:
```bash
# Check if MongoDB is running
mongo --eval "db.version()"
```

## Running the App 🎯

Simply run:
```bash
python main.py
```

The app will:
- Connect to MongoDB at `mongodb://localhost:27017/`
- Create a database called `pokemon_todo`
- Open a window with the Pokemon-style interface

## Creating an EXE File 📦

To create a standalone .exe file:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the executable:
```bash
pyinstaller --onefile --windowed --name="PokemonTodo" main.py
```

3. Find your .exe in the `dist` folder!

**Note:** When distributing the .exe, users still need MongoDB running locally.

### Alternative: Include Everything
To create an exe with a custom icon (optional):
```bash
pyinstaller --onefile --windowed --name="PokemonTodo" --icon=app_icon.ico main.py
```

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
