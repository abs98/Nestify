# Nestify

**Nestify** is a powerful Blender add-on for parenting and unparenting objects with enhanced controls via a quick-access pie menu. It allows you to group selected objects using empties at specific locations (world origin, active object, 3D cursor, etc.), ungroup or unparent them while optionally keeping transforms, and interactively adjust empty properties right in the viewport.

---

## ✨ Features

- 🧩 **Group (Parent) with Empty** at:
  - World origin
  - Active object location
  - Object center
  - 3D cursor

- 🔗 **Parent to Active** object (default parent)

- ❌ **Unparent** selected objects with:
  - Keep or reset transform
  - From any parent
  - From empties only

- 🎯 **Viewport Overlay & Interactive Controls**:
  - Interactive empty size & type adjustment (`E` key)
  - On-screen HUD overlay for selected empties

- ⚡️ **Pie Menu Access (Press `P`)**
  - Quick access to all grouping and ungrouping options

---

## 🔧 Installation

1. Download this repository as a ZIP file.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install** and select the ZIP file.
4. Enable the checkbox next to **Nestify** to activate it.

---

## 🖱️ Usage

- **P**: Open the parent/ungroup pie menu in Object Mode.
- **E**: While an empty is selected, press `E` to enter interactive mode for resizing and switching its display type.
  - Scroll Wheel = Change Empty Type
  - Move Mouse = Resize Empty
  - Confirm = Left Click / Space / Enter
  - Cancel = Right Click / Esc

---

## 📌 Pie Menu Options Overview

| Grouping Option           | Description                              |
|--------------------------|------------------------------------------|
| Group at Center          | Parents objects to an empty at average center |
| Group at Active          | Parents objects to empty at active object |
| Group at Cursor          | Parents objects to empty at 3D cursor    |
| Group at World Origin    | Parents objects to empty at world origin |

| Parenting / Unparenting Option       | Description                            |
|-------------------------------------|----------------------------------------|
| Parent                              | Parents selected to active object      |
| Unparent Selected (Keep/Reset)      | Clear parents only for selected        |
| Unparent from Object (Keep/Reset)   | Clear parent from any object parents   |
| Unparent from Empty (Keep/Reset)    | Clear parent and delete empty          |

---

## 💡 Notes

- Interactive overlays and input handling are automatically registered with the addon.
- Empty visual adjustments are non-destructive and convenient for organizing complex scenes.
- Designed to streamline object hierarchy editing and grouping in Blender.

---

## 📄 License

This add-on is open source under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Model verse**
https://www.youtube.com/@Model_verse

---
