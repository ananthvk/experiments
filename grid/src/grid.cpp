#include "grid.hpp"
#include <stdio.h>

void Grid::fill_cell_colors()
{
    if (!cell_colors.size())
    {
        cell_colors.resize(rows * cols, cell_color);
    }
}

void Grid::fill_hover_colors()
{
    if (!hover_colors.size())
    {
        hover_colors.resize(rows * cols, hover_color);
    }
}

void Grid::set_color(int row, int col, Color color)
{
    fill_cell_colors();
    cell_colors[row * rows + col] = color;
}

Color Grid::get_color(int row, int col)
{
    if (!cell_colors.size())
        return cell_color;
    return cell_colors[row * rows + col];
}

void Grid::set_hover_color(int row, int col, Color color)
{
    fill_hover_colors();
    hover_colors[row * rows + col] = color;
}

Color Grid::get_hover_color(int row, int col)
{
    if (!hover_colors.size())
        return hover_color;
    return hover_colors[row * rows + col];
}

void Grid::render(float offset_x, float offset_y)
{
    // Draw the cells and fill with cell color
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            Vector2 pos = {offset_x + (float)j * cell_size, offset_y + (float)i * cell_size};
            DrawRectangleV(pos, {(float)cell_size, (float)cell_size}, get_color(i, j));
            // Check if mouse is hovering above this cell
            if (CheckCollisionPointRec(GetMousePosition(),
                                       {pos.x, pos.y, (float)cell_size, (float)cell_size}))
            {
                if(on_hover)
                    on_hover(i, j);
                if (on_left_click && IsMouseButtonDown(MOUSE_BUTTON_LEFT))
                    on_left_click(i, j);
                if (on_right_click && IsMouseButtonDown(MOUSE_BUTTON_RIGHT))
                    on_right_click(i, j);

                DrawRectangleV(pos, {(float)cell_size, (float)cell_size}, get_hover_color(i, j));
            }
        }
    }
    // If there are n rows, n+1 lines should be drawn
    if (thickness_horizontal)
        for (int i = 0; i <= rows; i++)
        {
            DrawLineEx({offset_x, (float)i * cell_size + offset_y},
                       {offset_x + (float)cols * cell_size, offset_y + (float)i * cell_size},
                       thickness_horizontal, border_horizontal_color);
        }

    if (thickness_vertical)
        for (int i = 0; i <= cols; i++)
        {
            DrawLineEx({offset_x + (float)i * cell_size, offset_y},
                       {offset_x + (float)i * cell_size, offset_y + (float)rows * cell_size},
                       thickness_vertical, border_vertical_color);
        }
}

void Grid::render() { render(offset_x, offset_y); }

Grid::Grid()
    : rows(0), cols(0), cell_size(-1), cell_color(WHITE), hover_color(GREEN),
      border_horizontal_color(BLACK), border_vertical_color(BLACK), thickness_horizontal(0),
      thickness_vertical(0), offset_x(0), offset_y(0), on_left_click(nullptr),
      on_right_click(nullptr), on_hover(nullptr)
{
}

GridBuilder &GridBuilder::sides(int s)
{
    grid.rows = s;
    grid.cols = s;
    return *this;
}

GridBuilder &GridBuilder::rows(int r)
{
    grid.rows = r;
    return *this;
}

GridBuilder &GridBuilder::cols(int c)
{
    grid.cols = c;
    return *this;
}

GridBuilder &GridBuilder::cell_size(int sz)
{
    use_side_len = false;
    grid.cell_size = sz;
    return *this;
}

GridBuilder &GridBuilder::cell_color(Color col)
{
    grid.cell_color = col;
    return *this;
}

GridBuilder &GridBuilder::hover_color(Color col)
{
    grid.hover_color = col;
    return *this;
}

GridBuilder &GridBuilder::border_horizontal_color(Color col)
{
    grid.border_horizontal_color = col;
    return *this;
}

GridBuilder &GridBuilder::border_vertical_color(Color col)
{
    grid.border_vertical_color = col;
    return *this;
}

GridBuilder &GridBuilder::thickness_horizontal(float thickness)
{
    grid.thickness_horizontal = thickness;
    return *this;
}

GridBuilder &GridBuilder::thickness_vertical(float thickness)
{
    grid.thickness_vertical = thickness;
    return *this;
}

GridBuilder &GridBuilder::side_length(int length)
{
    side_len = length;
    use_side_len = true;
    return *this;
}

GridBuilder &GridBuilder::centered()
{
    is_centered = true;
    return *this;
}

Grid GridBuilder::build()
{
    if (use_side_len)
    {
        if (side_len == -1)
        {
            side_len = std::min(GetScreenHeight(), GetScreenWidth());
            if (is_centered)
                side_len = side_len / 2;
        }

        // Compute the cell size using side length
        grid.cell_size = side_len / std::max(grid.rows, grid.cols);
    }

    if (is_centered)
    {
        float x_mid = grid.rows * grid.cell_size / 2.0;
        float y_mid = grid.cols * grid.cell_size / 2.0;
        grid.offset_x = (GetScreenWidth() / 2.0) - x_mid;
        grid.offset_y = (GetScreenHeight() / 2.0) - y_mid;
    }

    return grid;
}