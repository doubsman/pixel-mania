# BID Editor

![BID Editor Splashscreen](ico/splash.png)

A pixel art editor specialized for BID (Binary Image Data) format files.

## Features

### File Operations
- Create new BID files
- Open existing BID files
- Save BID files
- Export as PNG/ASCII
- Auto-backup system

### Grid Management
- Adjustable grid size (5x5 to 96x96)
- Toggle grid display (Ctrl+G)
- Dynamic zoom (Ctrl+Mouse Wheel)
- Grid coordinates display

### Drawing Tools
- Freehand drawing mode
- Line tool
- Rectangle tool
- Circle tool
- Color palette
- Shape selector

### Selection Tools
- Rectangle selection
- Lasso selection
- Add to selection (Shift)
- Select all (Ctrl+A)
- Delete selection (Delete)

### Clipboard Operations
- Copy selection (Ctrl+C)
- Cut selection (Ctrl+X)
- Paste with preview (Ctrl+V)
- Multiple paste anchors

### Edit Operations
- Undo (Ctrl+Z)
- Redo (Ctrl+Y)
- Rotate selection (left/right)
- Flip selection (horizontal/vertical)
- Clear canvas

### View Features
- Thumbnail preview
- Real-time coordinates
- Selection size display
- Zoom level control
- Auto-scrolling

### Symbol Library
- Save custom symbols
- Load saved symbols
- Symbol preview

### build from source:
```bash
pyinstaller --noconfirm --onefile --add-data "ico;." --windowed --name bideditor editor.py
```

## Requirements
- Windows 7/10/11
- Screen resolution: 1024x768 minimum

## Keyboard Shortcuts

### File Operations
- Ctrl+M : Open Carrouselle files
- Ctrl+O : Open file
- Ctrl+S : Save file

### Edit Operations
- Ctrl+Z : Undo
- Ctrl+Y : Redo
- Delete : Delete selection
- Ctrl+A : Select all
- Esc : Cancel current operation

### Clipboard Operations
- Ctrl+C : Copy selection
- Ctrl+X : Cut selection
- Ctrl+V : Paste

### View Controls
- Ctrl+G : Toggle grid
- F11: Full-Screen
- Shift+Mouse Wheel: Horizontal scroll
- Mouse Wheel: Vertical scroll
- Ctrl+Mouse Wheel: Zoom in/out