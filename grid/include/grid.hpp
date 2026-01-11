#ifndef GRID_HPP
#define GRID_HPP
#include "raylib.h"
#include <vector>

class GridBuilder;
typedef void (*onclick_fptr)(const int &row, const int &col);

class Grid
{
    // All measurements are in pixels, top left corner is cell (0, 0)

    int rows, cols, cell_size;

    // When color of each cell is different
    std::vector<Color> cell_colors;
    std::vector<Color> hover_colors;

    // Common cell color for all cells
    Color cell_color;
    Color hover_color;
    Color border_horizontal_color;
    Color border_vertical_color;

    float thickness_horizontal;
    float thickness_vertical;

    float offset_x;
    float offset_y;

    void fill_cell_colors();
    void fill_hover_colors();

    onclick_fptr on_left_click;
    onclick_fptr on_right_click;
    onclick_fptr on_hover;


  public:
    Grid();

    void render(float offset_x, float offset_y);
    void render();
    void set_color(int row, int col, Color color);
    Color get_color(int row, int col);
    void set_hover_color(int row, int col, Color color);
    Color get_hover_color(int row, int col);
    friend class GridBuilder;

    void onclick_left(onclick_fptr fptr) { this->on_left_click = fptr; }

    void onclick_right(onclick_fptr fptr) { this->on_right_click = fptr; }

    void onhover(onclick_fptr fptr) { this->on_hover = fptr; }
};

class GridBuilder
{
    Grid grid;
    int side_len;
    bool use_side_len;
    bool is_centered;

  public:
    GridBuilder() : side_len(-1), use_side_len(true), is_centered(false) {}

    GridBuilder &sides(int s);
    GridBuilder &rows(int r);
    GridBuilder &cols(int c);
    GridBuilder &cell_size(int sz);
    GridBuilder &cell_color(Color col);
    GridBuilder &side_length(int length);
    GridBuilder &hover_color(Color col);
    GridBuilder &border_horizontal_color(Color col);
    GridBuilder &border_vertical_color(Color col);
    GridBuilder &thickness_horizontal(float thickness);
    GridBuilder &thickness_vertical(float thickness);
    GridBuilder &centered();
    Grid build();
};
#endif