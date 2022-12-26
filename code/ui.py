import osTimer
import utime
import modem
import sim
import lvgl as lv
import _thread
import gc
from machine import UART
from usr.common import Lock
from misc import PowerKey, Power
from usr.common import Abstract
from usr import EventMesh

# 界面风格
screen_style = lv.style_t()
screen_style.init()
screen_style.set_bg_color(lv.color_make(0x00, 0x00, 0x00))
screen_style.set_bg_opa(255)
# 白
style_bg = lv.style_t()
style_bg.init()
style_bg.set_radius(0)
style_bg.set_img_recolor(lv.color_make(0xff, 0xff, 0xff))
style_bg.set_img_recolor_opa(0)
style_bg.set_border_width(0)
style_bg.set_img_opa(255)
style_bg.set_pad_left(0)
style_bg.set_pad_right(0)
style_bg.set_pad_top(0)
style_bg.set_pad_bottom(0)
# line style
style_line = lv.style_t()
style_line.init()
style_line.set_line_color(lv.color_make(0xca, 0xca, 0xca))
style_line.set_line_width(1)
style_line.set_line_rounded(255)
# 白色思源14字体label样式 字距2
style_siyuan_white_14 = lv.style_t()
style_siyuan_white_14.init()
style_siyuan_white_14.set_radius(0)
style_siyuan_white_14.set_bg_color(lv.color_make(0x21, 0x95, 0xf6))
style_siyuan_white_14.set_bg_grad_color(lv.color_make(0x21, 0x95, 0xf6))
style_siyuan_white_14.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_siyuan_white_14.set_bg_opa(0)
style_siyuan_white_14.set_text_color(lv.color_make(0xca, 0xca, 0xca))
style_siyuan_white_14.set_text_font(lv.ali_14_font)
style_siyuan_white_14.set_anim_speed(20)
style_siyuan_white_14.set_text_letter_space(0)
style_siyuan_white_14.set_pad_left(0)
style_siyuan_white_14.set_pad_right(0)
style_siyuan_white_14.set_pad_top(0)
style_siyuan_white_14.set_pad_bottom(0)
# create style style_siyuan_14 黑色
style_siyuan_14_black = lv.style_t()
style_siyuan_14_black.init()
style_siyuan_14_black.set_radius(0)
style_siyuan_14_black.set_bg_color(lv.color_make(0x21, 0x95, 0xf6))
style_siyuan_14_black.set_bg_grad_color(lv.color_make(0x21, 0x95, 0xf6))
style_siyuan_14_black.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_siyuan_14_black.set_bg_opa(0)
style_siyuan_14_black.set_text_color(lv.color_make(0x00, 0x00, 0x00))
style_siyuan_14_black.set_text_font(lv.ali_14_font)
style_siyuan_14_black.set_text_letter_space(0)
style_siyuan_14_black.set_pad_left(0)
style_siyuan_14_black.set_pad_right(0)
style_siyuan_14_black.set_pad_top(0)
style_siyuan_14_black.set_pad_bottom(0)
# create style style_siyuan_11 黑色
style_siyuan_11_black = lv.style_t()
style_siyuan_11_black.init()
style_siyuan_11_black.set_radius(0)
style_siyuan_11_black.set_bg_color(lv.color_make(0x21, 0x95, 0xf6))
style_siyuan_11_black.set_bg_grad_color(lv.color_make(0x21, 0x95, 0xf6))
style_siyuan_11_black.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_siyuan_11_black.set_bg_opa(0)
style_siyuan_11_black.set_text_color(lv.color_make(0x00, 0x00, 0x00))
style_siyuan_11_black.set_text_font(lv.siyuan_light11_font)
style_siyuan_11_black.set_text_letter_space(0)
style_siyuan_11_black.set_pad_left(0)
style_siyuan_11_black.set_pad_right(0)
style_siyuan_11_black.set_pad_top(0)
style_siyuan_11_black.set_pad_bottom(0)
# 页眉容器样式
style_header = lv.style_t()
style_header.init()
style_header.set_radius(0)
style_header.set_bg_color(lv.color_make(0x5a, 0x61, 0x73))
style_header.set_bg_grad_color(lv.color_make(0x5a, 0x61, 0x73))
style_header.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_header.set_bg_opa(0)
style_header.set_border_color(lv.color_make(0x21, 0x95, 0xf6))
style_header.set_border_width(0)
style_header.set_border_opa(255)
style_header.set_pad_left(0)
style_header.set_pad_right(0)
style_header.set_pad_top(0)
style_header.set_pad_bottom(0)
# 黑色容器背景
style_cont_black = lv.style_t()
style_cont_black.init()
style_cont_black.set_radius(0)
style_cont_black.set_bg_color(lv.color_make(0x00, 0x00, 0x00))
style_cont_black.set_bg_grad_color(lv.color_make(0x00, 0x00, 0x00))
style_cont_black.set_anim_speed(20)
style_cont_black.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_cont_black.set_bg_opa(255)
style_cont_black.set_border_width(0)
style_cont_black.set_pad_left(0)
style_cont_black.set_pad_right(0)
style_cont_black.set_pad_top(0)
style_cont_black.set_pad_bottom(0)
# create style style_list_scrollbar
style_list_scrollbar = lv.style_t()
style_list_scrollbar.init()
style_list_scrollbar.set_radius(3)
style_list_scrollbar.set_bg_color(lv.color_make(0xff, 0xff, 0xff))
style_list_scrollbar.set_bg_grad_color(lv.color_make(0xff, 0xff, 0xff))
style_list_scrollbar.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_list_scrollbar.set_bg_opa(0)
# 群组label 样式
style_group_label_black = lv.style_t()
style_group_label_black.init()
style_group_label_black.set_anim_speed(20)
# 群组列表样式 黑色
style_group_black = lv.style_t()
style_group_black.init()
style_group_black.set_radius(0)
style_group_black.set_bg_color(lv.color_make(0x00, 0x00, 0x00))
style_group_black.set_bg_grad_color(lv.color_make(0x00, 0x00, 0x00))
style_group_black.set_anim_speed(10)
style_group_black.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_group_black.set_border_width(0)
style_group_black.set_bg_opa(255)
style_group_black.set_pad_left(0)
style_group_black.set_pad_right(0)
style_group_black.set_pad_top(0)
style_group_black.set_pad_bottom(0)
style_group_black.set_text_color(lv.color_make(0xca, 0xca, 0xca))
style_group_black.set_text_font(lv.ali_14_font)
# 成员列表样式 蓝色
style_group_blue = lv.style_t()
style_group_blue.init()
style_group_blue.set_radius(0)
style_group_blue.set_bg_color(lv.color_make(0x28, 0x3d, 0xe2))
style_group_blue.set_bg_grad_color(lv.color_make(0x28, 0x3d, 0xe2))
style_group_blue.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_group_blue.set_bg_opa(255)
style_group_blue.set_border_width(0)
style_group_blue.set_pad_left(0)
style_group_blue.set_pad_right(0)
style_group_blue.set_pad_top(0)
style_group_blue.set_pad_bottom(0)
style_group_blue.set_text_color(lv.color_make(0xff, 0xff, 0xff))
style_group_blue.set_text_font(lv.ali_14_font)
# 成员列表样式 红色
style_group_red = lv.style_t()
style_group_red.init()
style_group_red.set_radius(0)
style_group_red.set_bg_color(lv.color_make(0xdc, 0x1e, 0x1e))
style_group_red.set_bg_grad_color(lv.color_make(0xdc, 0x1e, 0x1e))
style_group_red.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_group_red.set_bg_opa(255)
style_group_red.set_border_width(0)
style_group_red.set_pad_left(0)
style_group_red.set_pad_right(0)
style_group_red.set_pad_top(0)
style_group_red.set_pad_bottom(0)
style_group_red.set_text_color(lv.color_make(0xff, 0xff, 0xff))
style_group_red.set_text_font(lv.ali_14_font)
# 成员列表样式 黄色
style_group_yellow = lv.style_t()
style_group_yellow.init()
style_group_yellow.set_radius(0)
style_group_yellow.set_bg_color(lv.color_make(0xe6, 0x91, 0x00))
style_group_yellow.set_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00))
style_group_yellow.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_group_yellow.set_border_width(0)
style_group_yellow.set_bg_opa(255)
style_group_yellow.set_pad_left(0)
style_group_yellow.set_pad_right(0)
style_group_yellow.set_pad_top(0)
style_group_yellow.set_pad_bottom(0)
style_group_yellow.set_text_color(lv.color_make(0xff, 0xff, 0xff))
style_group_yellow.set_text_font(lv.ali_14_font)
# 成员列表样式 白色
style_group_white = lv.style_t()
style_group_white.init()
style_group_white.set_radius(0)
style_group_white.set_bg_color(lv.color_make(0xff, 0xff, 0xff))
style_group_white.set_bg_grad_color(lv.color_make(0xff, 0xff, 0xff))
style_group_white.set_anim_speed(20)
style_group_white.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_group_white.set_bg_opa(255)
style_group_white.set_border_width(0)
style_group_white.set_pad_left(0)
style_group_white.set_pad_right(0)
style_group_white.set_pad_top(0)
style_group_white.set_pad_bottom(0)
style_group_white.set_text_color(lv.color_make(0xca, 0xca, 0xca))
style_group_white.set_text_font(lv.ali_14_font)
################################# welcome页面 #########################################
welcome = lv.obj()
welcome.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
welcome_bg = lv.img(welcome)
welcome_bg.set_pos(0, 0)
welcome_bg.set_size(128, 128)
welcome_bg.set_src("B:/static/index.png")
welcome_bg.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
lv.scr_load(welcome)
################################# main主页面 #########################################
main_screen = lv.obj()
main_screen.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
main_screen.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
main_cont_top = lv.obj(main_screen)
main_cont_top.set_pos(0, 0)
main_cont_top.set_size(128, 20)
main_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
main_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
main_top_battery = lv.img(main_cont_top)
main_top_battery.set_pos(109, 5)
main_top_battery.set_size(16, 13)
main_top_battery.set_src('B:/static/battery_4.png')
main_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_top_gps = lv.img(main_cont_top)
main_top_gps.set_pos(50, 4)
main_top_gps.set_size(14, 14)
main_top_gps.set_src('B:/static/gps.png')
main_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_top_ej_img = lv.img(main_cont_top)
main_top_ej_img.set_pos(93, 5)
main_top_ej_img.set_size(14, 14)
main_top_ej_img.set_src('B:/static/earphone1.png')
main_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_top_sim_id = lv.img(main_cont_top)
main_top_sim_id.set_pos(36, 4)
main_top_sim_id.set_size(14, 14)
main_top_sim_id.set_src('B:/static/1.png')
main_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_top_signal = lv.img(main_cont_top)
main_top_signal.set_pos(2, 2)
main_top_signal.set_size(16, 16)
main_top_signal.set_src('B:/static/signal_5.png')
main_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_top_net = lv.label(main_cont_top)
main_top_net.set_pos(18, 4)
main_top_net.set_size(20, 11)
main_top_net.set_text("4G")
main_top_net.set_long_mode(lv.label.LONG.WRAP)
main_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
main_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
main_cont_list = lv.obj(main_screen)
main_cont_list.set_pos(0, 20)
main_cont_list.set_size(128, 89)
line_points = [
    {"x": 0, "y": 0},
    {"x": 128, "y": 0},
]
main_cont_line_1 = lv.line(main_screen)
main_cont_line_1.set_pos(0, 42)  # 22
main_cont_line_1.set_size(128, 1)
main_cont_line_1.set_points(line_points, 2)
main_cont_line_1.add_style(style_line, lv.PART.MAIN | lv.STATE.DEFAULT)
main_cont_line_2 = lv.line(main_screen)
main_cont_line_2.set_pos(0, 64)
main_cont_line_2.set_size(128, 1)
main_cont_line_2.set_points(line_points, 2)
main_cont_line_2.add_style(style_line, lv.PART.MAIN | lv.STATE.DEFAULT)
main_cont_line_3 = lv.line(main_screen)
main_cont_line_3.set_pos(0, 86)
main_cont_line_3.set_size(128, 1)
main_cont_line_3.set_points(line_points, 2)
main_cont_line_3.add_style(style_line, lv.PART.MAIN | lv.STATE.DEFAULT)
main_cont_line_4 = lv.line(main_screen)
main_cont_line_4.set_pos(0, 108)
main_cont_line_4.set_size(128, 1)
main_cont_line_4.set_points(line_points, 2)
main_cont_line_4.add_style(style_line, lv.PART.MAIN | lv.STATE.DEFAULT)
main_cont_list.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
# 使用者
main_user_id_label = lv.label(main_cont_list)  # 使用者
main_user_id_label.set_pos(30, 3)
main_user_id_label.set_size(97, 20)
main_user_id_label.set_text("")
main_user_id_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
main_user_id_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
main_user_id_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
main_user_id_img = lv.img(main_cont_list)
main_user_id_img.set_pos(7, 2)
main_user_id_img.set_size(19, 19)
main_user_id_img.set_src('B:/static/member_black.png')
main_user_id_img.set_pivot(0, 0)
main_user_id_img.set_angle(0)
main_user_id_img.add_flag(lv.obj.FLAG.CLICKABLE)
main_user_id_label.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_member_label = lv.label(main_cont_list)  # 群组
main_member_label.set_pos(30, 26)
main_member_label.set_size(97, 20)
main_member_label.set_text("")
main_member_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
main_member_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
main_member_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
main_member_img = lv.img(main_cont_list)
main_member_img.set_pos(7, 25)
main_member_img.set_size(19, 19)
main_member_img.set_src('B:/static/group_black.png')
main_member_img.set_pivot(0, 0)
main_member_img.set_angle(0)
main_member_img.add_flag(lv.obj.FLAG.CLICKABLE)
main_member_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_operator_label = lv.label(main_cont_list)  # 运营商
main_operator_label.set_pos(30, 48)
main_operator_label.set_size(97, 20)
main_operator_label.set_text("")
main_operator_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
main_operator_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
main_operator_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
main_operator_img = lv.img(main_cont_list)
main_operator_img.set_pos(7, 46)
main_operator_img.set_size(19, 19)
main_operator_img.set_src('B:/static/operator.png')
main_operator_img.set_pivot(0, 0)
main_operator_img.set_angle(0)
main_operator_img.add_flag(lv.obj.FLAG.CLICKABLE)
main_operator_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
main_weather_label = lv.label(main_cont_list)  # 话权状态
main_weather_label.set_pos(30, 70)
main_weather_label.set_size(97, 19)
main_weather_label.set_text("")
main_weather_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
main_weather_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
main_weather_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
main_weather_img = lv.img(main_cont_list)
main_weather_img.set_pos(7, 68)
main_weather_img.set_size(19, 19)
main_weather_img.set_src('B:/static/weather.png')
main_weather_img.set_pivot(0, 0)
main_weather_img.set_angle(0)
main_weather_img.add_flag(lv.obj.FLAG.CLICKABLE)
main_weather_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
# 底部content
main_cont_bottom = lv.obj(main_screen)
main_cont_bottom.set_pos(0, 113)
main_cont_bottom.set_size(128, 19)
main_bottom_date_label = lv.label(main_cont_bottom)
main_bottom_date_label.set_pos(2, 0)
main_bottom_date_label.set_size(97, 11)
main_bottom_date_label.set_text("")
main_bottom_time_label = lv.label(main_cont_bottom)
main_bottom_time_label.set_pos(90, 0)
main_bottom_time_label.set_size(38, 11)
main_bottom_time_label.set_text("")
main_bottom_time_label.set_long_mode(lv.label.LONG.WRAP)
main_bottom_date_label.set_long_mode(lv.label.LONG.WRAP)
main_bottom_time_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
main_bottom_date_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
main_bottom_date_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
main_bottom_time_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
main_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# ####################################################################### 菜单页面 #
menu_screen = lv.obj()
menu_screen.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
menu_cont_top = lv.obj(menu_screen)
menu_cont_top.set_pos(0, 0)
menu_cont_top.set_size(128, 20)
menu_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
menu_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_top_battery = lv.img(menu_cont_top)
menu_top_battery.set_pos(109, 5)
menu_top_battery.set_size(16, 13)
menu_top_battery.set_src('B:/static/battery_4.png')
menu_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_top_gps = lv.img(menu_cont_top)
menu_top_gps.set_pos(50, 4)
menu_top_gps.set_size(14, 14)
menu_top_gps.set_src('B:/static/gps.png')
menu_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_top_ej_img = lv.img(menu_cont_top)
menu_top_ej_img.set_pos(93, 5)
menu_top_ej_img.set_size(14, 14)
menu_top_ej_img.set_src('B:/static/earphone1.png')
menu_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_top_sim_id = lv.img(menu_cont_top)
menu_top_sim_id.set_pos(36, 4)
menu_top_sim_id.set_size(14, 14)
menu_top_sim_id.set_src('B:/static/1.png')
menu_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_top_signal = lv.img(menu_cont_top)
menu_top_signal.set_pos(2, 2)
menu_top_signal.set_size(16, 16)
menu_top_signal.set_src('B:/static/signal_5.png')
menu_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_top_net = lv.label(menu_cont_top)
menu_top_net.set_pos(18, 4)
menu_top_net.set_size(20, 11)
menu_top_net.set_text("4G")
menu_top_net.set_long_mode(lv.label.LONG.WRAP)
menu_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
menu_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_list = lv.list(menu_screen)
menu_screen_list.set_pos(0, 20)
menu_screen_list.set_size(128, 87)
menu_screen_list.set_style_pad_left(2, 0)
menu_screen_list.set_style_pad_top(4, 0)
menu_screen_list.set_style_pad_row(3, 0)
menu_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
menu_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
menu_screen_btn = lv.btn(menu_screen_list)
menu_screen_btn.set_pos(20, 0)
menu_screen_btn.set_size(128, 18)
menu_screen_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_img = lv.img(menu_screen_btn)
menu_screen_img.set_pos(0, 0)
menu_screen_img.set_size(19, 18)
menu_screen_img.set_src('B:/static/group_black.png')
menu_screen_label = lv.label(menu_screen_btn)
menu_screen_label.set_pos(25, 1)
menu_screen_label.set_size(105, 18)
menu_screen_label.set_text("群组")
menu_screen_btn1 = lv.btn(menu_screen_list)
menu_screen_btn1.set_pos(20, 0)
menu_screen_btn1.set_size(128, 18)
menu_screen_btn1.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_img1 = lv.img(menu_screen_btn1)
menu_screen_img1.set_pos(0, 0)
menu_screen_img1.set_size(19, 18)
menu_screen_img1.set_src('B:/static/member_black.png')
menu_screen_label1 = lv.label(menu_screen_btn1)
menu_screen_label1.set_pos(25, 1)
menu_screen_label1.set_size(105, 18)
menu_screen_label1.set_text("成员")
menu_screen_btn2 = lv.btn(menu_screen_list)
menu_screen_btn2.set_pos(20, 0)
menu_screen_btn2.set_size(128, 18)
menu_screen_btn2.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_img2 = lv.img(menu_screen_btn2)
menu_screen_img2.set_pos(0, 0)
menu_screen_img2.set_size(19, 18)
menu_screen_img2.set_src('B:/static/weather.png')
menu_screen_label2 = lv.label(menu_screen_btn2)
menu_screen_label2.set_pos(25, 1)
menu_screen_label2.set_size(105, 18)
menu_screen_label2.set_text("天气预报")
menu_screen_btn3 = lv.btn(menu_screen_list)
menu_screen_btn3.set_pos(20, 0)
menu_screen_btn3.set_size(128, 18)
menu_screen_btn3.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_img3 = lv.img(menu_screen_btn3)
menu_screen_img3.set_pos(0, 0)
menu_screen_img3.set_size(19, 18)
menu_screen_img3.set_src('B:/static/location.png')
menu_screen_label3 = lv.label(menu_screen_btn3)
menu_screen_label3.set_pos(25, 1)
menu_screen_label3.set_size(105, 18)
menu_screen_label3.set_text("我的位置")
menu_screen_btn4 = lv.btn(menu_screen_list)
menu_screen_btn4.set_pos(20, 0)
menu_screen_btn4.set_size(128, 18)
menu_screen_btn4.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_img4 = lv.img(menu_screen_btn4)
menu_screen_img4.set_pos(0, 0)
menu_screen_img4.set_size(19, 18)
menu_screen_img4.set_src('B:/static/setting.png')
menu_screen_label4 = lv.label(menu_screen_btn4)
menu_screen_label4.set_pos(25, 1)
menu_screen_label4.set_size(105, 18)
menu_screen_label4.set_text("设置")
menu_screen_btn5 = lv.btn(menu_screen_list)
menu_screen_btn5.set_pos(20, 0)
menu_screen_btn5.set_size(128, 18)
menu_screen_btn5.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_screen_img5 = lv.img(menu_screen_btn5)
menu_screen_img5.set_pos(0, 0)
menu_screen_img5.set_size(19, 18)
menu_screen_img5.set_src('B:/static/my.png')
menu_screen_label5 = lv.label(menu_screen_btn5)
menu_screen_label5.set_pos(25, 1)
menu_screen_label5.set_size(105, 18)
menu_screen_label5.set_text("系统")
menu_cont_bottom = lv.obj(menu_screen)
menu_cont_bottom.set_pos(0, 111)
menu_cont_bottom.set_size(128, 19)
menu_bottom_label = lv.label(menu_cont_bottom)
menu_bottom_label.set_pos(25, 0)
menu_bottom_label.set_size(103, 19)
menu_bottom_label.set_text("")
menu_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
menu_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
menu_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_bottom_img = lv.img(menu_cont_bottom)
menu_bottom_img.set_pos(5, 0)
menu_bottom_img.set_size(15, 16)
menu_bottom_img.set_src('B:/static/menber.png')
menu_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
menu_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# ####################################################################### 菜单页面 #
# 群组
group = lv.obj()
group.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
group.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
group_cont_top = lv.obj(group)
group_cont_top.set_pos(0, 0)
group_cont_top.set_size(128, 20)
group_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
group_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
group_top_battery = lv.img(group_cont_top)
group_top_battery.set_pos(109, 5)
group_top_battery.set_size(16, 13)
group_top_battery.set_src('B:/static/battery_4.png')
group_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
group_top_gps = lv.img(group_cont_top)
group_top_gps.set_pos(50, 4)
group_top_gps.set_size(14, 14)
group_top_gps.set_src('B:/static/gps.png')
group_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
group_top_ej_img = lv.img(group_cont_top)
group_top_ej_img.set_pos(93, 5)
group_top_ej_img.set_size(14, 14)
group_top_ej_img.set_src('B:/static/earphone1.png')
group_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
group_top_sim_id = lv.img(group_cont_top)
group_top_sim_id.set_pos(36, 4)
group_top_sim_id.set_size(14, 14)
group_top_sim_id.set_src('B:/static/1.png')
group_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
group_top_signal = lv.img(group_cont_top)
group_top_signal.set_pos(2, 2)
group_top_signal.set_size(16, 16)
group_top_signal.set_src('B:/static/signal_5.png')
group_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
group_top_net = lv.label(group_cont_top)
group_top_net.set_pos(18, 4)
group_top_net.set_size(20, 11)
group_top_net.set_text("4G")
group_top_net.set_long_mode(lv.label.LONG.WRAP)
group_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
group_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
group_screen_list = lv.list(group)
group_screen_list.set_pos(0, 20)
group_screen_list.set_size(128, 89)
group_screen_list.set_style_pad_left(2, 0)
group_screen_list.set_style_pad_top(4, 0)
group_screen_list.set_style_pad_row(3, 0)
group_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
group_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
group_cont_bottom = lv.obj(group)
group_cont_bottom.set_pos(0, 111)
group_cont_bottom.set_size(128, 19)
group_bottom_label = lv.label(group_cont_bottom)
group_bottom_label.set_pos(25, 0)
group_bottom_label.set_size(103, 19)
group_bottom_label.set_text("")
group_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
group_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
group_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
group_bottom_img = lv.img(group_cont_bottom)
group_bottom_img.set_pos(5, 0)
group_bottom_img.set_size(15, 16)
group_bottom_img.set_src('B:/static/menber.png')
group_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
group_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 成员界面
member = lv.obj()
member.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
member.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
member_cont_top = lv.obj(member)
member_cont_top.set_pos(0, 0)
member_cont_top.set_size(128, 20)
member_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
member_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
member_top_battery = lv.img(member_cont_top)
member_top_battery.set_pos(109, 5)
member_top_battery.set_size(16, 13)
member_top_battery.set_src('B:/static/battery_4.png')
member_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
member_top_gps = lv.img(member_cont_top)
member_top_gps.set_pos(50, 4)
member_top_gps.set_size(14, 14)
member_top_gps.set_src('B:/static/gps.png')
member_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
member_top_ej_img = lv.img(member_cont_top)
member_top_ej_img.set_pos(93, 5)
member_top_ej_img.set_size(14, 14)
member_top_ej_img.set_src('B:/static/earphone1.png')
member_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
member_top_sim_id = lv.img(member_cont_top)
member_top_sim_id.set_pos(36, 4)
member_top_sim_id.set_size(14, 14)
member_top_sim_id.set_src('B:/static/1.png')
member_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
member_top_signal = lv.img(member_cont_top)
member_top_signal.set_pos(2, 2)
member_top_signal.set_size(16, 16)
member_top_signal.set_src('B:/static/signal_5.png')
member_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
member_top_net = lv.label(member_cont_top)
member_top_net.set_pos(18, 4)
member_top_net.set_size(20, 11)
member_top_net.set_text("4G")
member_top_net.set_long_mode(lv.label.LONG.WRAP)
member_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
member_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
member_screen_list = lv.list(member)
member_screen_list.set_pos(0, 20)
member_screen_list.set_size(128, 89)
member_screen_list.set_style_pad_left(2, 0)
member_screen_list.set_style_pad_top(4, 0)
member_screen_list.set_style_pad_row(3, 0)
member_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
member_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR)
member_cont_bottom = lv.obj(member)
member_cont_bottom.set_pos(0, 111)
member_cont_bottom.set_size(128, 19)
member_bottom_label = lv.label(member_cont_bottom)
member_bottom_label.set_pos(25, 0)
member_bottom_label.set_size(103, 19)
member_bottom_label.set_text("")
member_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
member_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
member_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
member_bottom_img = lv.img(member_cont_bottom)
member_bottom_img.set_pos(5, 0)
member_bottom_img.set_size(15, 16)
member_bottom_img.set_src('B:/static/menber.png')
member_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
member_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 设置页面
setting = lv.obj()
setting.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_cont_top = lv.obj(setting)
setting_cont_top.set_pos(0, 0)
setting_cont_top.set_size(128, 20)
setting_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_top_battery = lv.img(setting_cont_top)
setting_top_battery.set_pos(109, 5)
setting_top_battery.set_size(16, 13)
setting_top_battery.set_src('B:/static/battery_4.png')
setting_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_top_gps = lv.img(setting_cont_top)
setting_top_gps.set_pos(50, 4)
setting_top_gps.set_size(14, 14)
setting_top_gps.set_src('B:/static/gps.png')
setting_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_top_ej_img = lv.img(setting_cont_top)
setting_top_ej_img.set_pos(93, 5)
setting_top_ej_img.set_size(14, 14)
setting_top_ej_img.set_src('B:/static/earphone1.png')
setting_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_top_sim_id = lv.img(setting_cont_top)
setting_top_sim_id.set_pos(36, 4)
setting_top_sim_id.set_size(14, 14)
setting_top_sim_id.set_src('B:/static/1.png')
setting_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_top_signal = lv.img(setting_cont_top)
setting_top_signal.set_pos(2, 2)
setting_top_signal.set_size(16, 16)
setting_top_signal.set_src('B:/static/signal_5.png')
setting_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_top_net = lv.label(setting_cont_top)
setting_top_net.set_pos(18, 4)
setting_top_net.set_size(20, 11)
setting_top_net.set_text("4G")
setting_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_screen_list = lv.list(setting)
setting_screen_list.set_pos(0, 20)
setting_screen_list.set_size(128, 89)
setting_screen_list.set_style_pad_left(2, 0)
setting_screen_list.set_style_pad_top(4, 0)
setting_screen_list.set_style_pad_row(3, 0)
setting_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_cont_bottom = lv.obj(setting)
setting_cont_bottom.set_pos(0, 111)
setting_cont_bottom.set_size(128, 19)
setting_bottom_label = lv.label(setting_cont_bottom)
setting_bottom_label.set_pos(25, 0)
setting_bottom_label.set_size(103, 19)
setting_bottom_label.set_text("")
setting_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_bottom_img = lv.img(setting_cont_bottom)
setting_bottom_img.set_pos(5, 0)
setting_bottom_img.set_size(15, 16)
setting_bottom_img.set_src('B:/static/menber.png')
setting_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 息屏时间页面
setting_rest_screen = lv.obj()
setting_rest_screen.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_screen.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_rest_cont_top = lv.obj(setting_rest_screen)
setting_rest_cont_top.set_pos(0, 0)
setting_rest_cont_top.set_size(128, 20)
setting_rest_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_rest_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_top_battery = lv.img(setting_rest_cont_top)
setting_rest_top_battery.set_pos(109, 5)
setting_rest_top_battery.set_size(16, 13)
setting_rest_top_battery.set_src('B:/static/battery_4.png')
setting_rest_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_top_gps = lv.img(setting_rest_cont_top)
setting_rest_top_gps.set_pos(50, 4)
setting_rest_top_gps.set_size(14, 14)
setting_rest_top_gps.set_src('B:/static/gps.png')
setting_rest_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_top_ej_img = lv.img(setting_rest_cont_top)
setting_rest_top_ej_img.set_pos(93, 5)
setting_rest_top_ej_img.set_size(14, 14)
setting_rest_top_ej_img.set_src('B:/static/earphone1.png')
setting_rest_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_top_sim_id = lv.img(setting_rest_cont_top)
setting_rest_top_sim_id.set_pos(36, 4)
setting_rest_top_sim_id.set_size(14, 14)
setting_rest_top_sim_id.set_src('B:/static/1.png')
setting_rest_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_top_signal = lv.img(setting_rest_cont_top)
setting_rest_top_signal.set_pos(2, 2)
setting_rest_top_signal.set_size(16, 16)
setting_rest_top_signal.set_src('B:/static/signal_5.png')
setting_rest_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_top_net = lv.label(setting_rest_cont_top)
setting_rest_top_net.set_pos(18, 4)
setting_rest_top_net.set_size(20, 11)
setting_rest_top_net.set_text("4G")
setting_rest_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_rest_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_rest_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_screen_label_1 = lv.label(setting_rest_screen)
setting_rest_screen_label_1.set_pos(5, 25)
setting_rest_screen_label_1.set_size(103, 20)
setting_rest_screen_label_1.set_text("息屏时间设置")
setting_rest_screen_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_rest_screen_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_rest_screen_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_screen_screen_list = lv.list(setting_rest_screen)
setting_rest_screen_screen_list.set_pos(0, 40)
setting_rest_screen_screen_list.set_size(128, 69)
setting_rest_screen_screen_list.set_style_pad_left(2, 0)
setting_rest_screen_screen_list.set_style_pad_top(4, 0)
setting_rest_screen_screen_list.set_style_pad_row(3, 0)
setting_rest_screen_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_screen_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_rest_screen_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_rest_cont_bottom = lv.obj(setting_rest_screen)
setting_rest_cont_bottom.set_pos(0, 111)
setting_rest_cont_bottom.set_size(128, 19)
setting_rest_bottom_label = lv.label(setting_rest_cont_bottom)
setting_rest_bottom_label.set_pos(25, 0)
setting_rest_bottom_label.set_size(103, 19)
setting_rest_bottom_label.set_text("")
setting_rest_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_rest_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_rest_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_bottom_img = lv.img(setting_rest_cont_bottom)
setting_rest_bottom_img.set_pos(5, 0)
setting_rest_bottom_img.set_size(15, 16)
setting_rest_bottom_img.set_src('B:/static/menber.png')
setting_rest_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_rest_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 单呼退出
setting_call_time = lv.obj()
setting_call_time.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_call_time_cont_top = lv.obj(setting_call_time)
setting_call_time_cont_top.set_pos(0, 0)
setting_call_time_cont_top.set_size(128, 20)
setting_call_time_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_call_time_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_top_battery = lv.img(setting_call_time_cont_top)
setting_call_time_top_battery.set_pos(109, 5)
setting_call_time_top_battery.set_size(16, 13)
setting_call_time_top_battery.set_src('B:/static/battery_4.png')
setting_call_time_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_top_gps = lv.img(setting_call_time_cont_top)
setting_call_time_top_gps.set_pos(50, 4)
setting_call_time_top_gps.set_size(14, 14)
setting_call_time_top_gps.set_src('B:/static/gps.png')
setting_call_time_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_top_ej_img = lv.img(setting_call_time_cont_top)
setting_call_time_top_ej_img.set_pos(93, 5)
setting_call_time_top_ej_img.set_size(14, 14)
setting_call_time_top_ej_img.set_src('B:/static/earphone1.png')
setting_call_time_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_top_sim_id = lv.img(setting_call_time_cont_top)
setting_call_time_top_sim_id.set_pos(36, 4)
setting_call_time_top_sim_id.set_size(14, 14)
setting_call_time_top_sim_id.set_src('B:/static/1.png')
setting_call_time_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_top_signal = lv.img(setting_call_time_cont_top)
setting_call_time_top_signal.set_pos(2, 2)
setting_call_time_top_signal.set_size(16, 16)
setting_call_time_top_signal.set_src('B:/static/signal_5.png')
setting_call_time_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_top_net = lv.label(setting_call_time_cont_top)
setting_call_time_top_net.set_pos(18, 4)
setting_call_time_top_net.set_size(20, 11)
setting_call_time_top_net.set_text("4G")
setting_call_time_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_call_time_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_call_time_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_label_1 = lv.label(setting_call_time)
setting_call_time_label_1.set_pos(5, 25)
setting_call_time_label_1.set_size(103, 20)
setting_call_time_label_1.set_text("单呼退出时间")
setting_call_time_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_call_time_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_call_time_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_screen_list = lv.list(setting_call_time)
setting_call_time_screen_list.set_pos(0, 40)
setting_call_time_screen_list.set_size(128, 69)
setting_call_time_screen_list.set_style_pad_left(2, 0)
setting_call_time_screen_list.set_style_pad_top(4, 0)
setting_call_time_screen_list.set_style_pad_row(3, 0)
setting_call_time_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_call_time_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_call_time_cont_bottom = lv.obj(setting_call_time)
setting_call_time_cont_bottom.set_pos(0, 111)
setting_call_time_cont_bottom.set_size(128, 19)
setting_call_time_bottom_label = lv.label(setting_call_time_cont_bottom)
setting_call_time_bottom_label.set_pos(25, 0)
setting_call_time_bottom_label.set_size(103, 19)
setting_call_time_bottom_label.set_text("")
setting_call_time_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_call_time_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_call_time_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_bottom_img = lv.img(setting_call_time_cont_bottom)
setting_call_time_bottom_img.set_pos(5, 0)
setting_call_time_bottom_img.set_size(15, 16)
setting_call_time_bottom_img.set_src('B:/static/menber.png')
setting_call_time_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_call_time_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 省电模式设置
setting_battery = lv.obj()
setting_battery.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_battery_cont_top = lv.obj(setting_battery)
setting_battery_cont_top.set_pos(0, 0)
setting_battery_cont_top.set_size(128, 20)
setting_battery_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_battery_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_top_battery = lv.img(setting_battery_cont_top)
setting_battery_top_battery.set_pos(109, 5)
setting_battery_top_battery.set_size(16, 13)
setting_battery_top_battery.set_src('B:/static/battery_4.png')
setting_battery_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_top_gps = lv.img(setting_battery_cont_top)
setting_battery_top_gps.set_pos(50, 4)
setting_battery_top_gps.set_size(14, 14)
setting_battery_top_gps.set_src('B:/static/gps.png')
setting_battery_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_top_ej_img = lv.img(setting_battery_cont_top)
setting_battery_top_ej_img.set_pos(93, 5)
setting_battery_top_ej_img.set_size(14, 14)
setting_battery_top_ej_img.set_src('B:/static/earphone1.png')
setting_battery_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_top_sim_id = lv.img(setting_battery_cont_top)
setting_battery_top_sim_id.set_pos(36, 4)
setting_battery_top_sim_id.set_size(14, 14)
setting_battery_top_sim_id.set_src('B:/static/1.png')
setting_battery_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_top_signal = lv.img(setting_battery_cont_top)
setting_battery_top_signal.set_pos(2, 2)
setting_battery_top_signal.set_size(16, 16)
setting_battery_top_signal.set_src('B:/static/signal_5.png')
setting_battery_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_top_net = lv.label(setting_battery_cont_top)
setting_battery_top_net.set_pos(18, 4)
setting_battery_top_net.set_size(20, 11)
setting_battery_top_net.set_text("4G")
setting_battery_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_battery_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_battery_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_label_1 = lv.label(setting_battery)
setting_battery_label_1.set_pos(5, 25)
setting_battery_label_1.set_size(103, 20)
setting_battery_label_1.set_text("省电模式")
setting_battery_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_battery_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_battery_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_screen_list = lv.list(setting_battery)
setting_battery_screen_list.set_pos(0, 40)
setting_battery_screen_list.set_size(128, 69)
setting_battery_screen_list.set_style_pad_left(2, 0)
setting_battery_screen_list.set_style_pad_top(4, 0)
setting_battery_screen_list.set_style_pad_row(3, 0)
setting_battery_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_battery_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_battery_cont_bottom = lv.obj(setting_battery)
setting_battery_cont_bottom.set_pos(0, 111)
setting_battery_cont_bottom.set_size(128, 19)
setting_battery_bottom_label = lv.label(setting_battery_cont_bottom)
setting_battery_bottom_label.set_pos(25, 0)
setting_battery_bottom_label.set_size(103, 19)
setting_battery_bottom_label.set_text("")
setting_battery_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_battery_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_battery_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_bottom_img = lv.img(setting_battery_cont_bottom)
setting_battery_bottom_img.set_pos(5, 0)
setting_battery_bottom_img.set_size(15, 16)
setting_battery_bottom_img.set_src('B:/static/menber.png')
setting_battery_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_battery_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# SIM卡设置
setting_sim = lv.obj()
setting_sim.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_sim_cont_top = lv.obj(setting_sim)
setting_sim_cont_top.set_pos(0, 0)
setting_sim_cont_top.set_size(128, 20)
setting_sim_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_sim_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_top_battery = lv.img(setting_sim_cont_top)
setting_sim_top_battery.set_pos(109, 5)
setting_sim_top_battery.set_size(16, 13)
setting_sim_top_battery.set_src('B:/static/battery_4.png')
setting_sim_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_top_gps = lv.img(setting_sim_cont_top)
setting_sim_top_gps.set_pos(50, 4)
setting_sim_top_gps.set_size(14, 14)
setting_sim_top_gps.set_src('B:/static/gps.png')
setting_sim_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_top_ej_img = lv.img(setting_sim_cont_top)
setting_sim_top_ej_img.set_pos(93, 5)
setting_sim_top_ej_img.set_size(14, 14)
setting_sim_top_ej_img.set_src('B:/static/earphone1.png')
setting_sim_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_top_sim_id = lv.img(setting_sim_cont_top)
setting_sim_top_sim_id.set_pos(36, 4)
setting_sim_top_sim_id.set_size(14, 14)
setting_sim_top_sim_id.set_src('B:/static/1.png')
setting_sim_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_top_signal = lv.img(setting_sim_cont_top)
setting_sim_top_signal.set_pos(2, 2)
setting_sim_top_signal.set_size(16, 16)
setting_sim_top_signal.set_src('B:/static/signal_5.png')
setting_sim_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_top_net = lv.label(setting_sim_cont_top)
setting_sim_top_net.set_pos(18, 4)
setting_sim_top_net.set_size(20, 11)
setting_sim_top_net.set_text("4G")
setting_sim_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_sim_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_sim_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_label_1 = lv.label(setting_sim)
setting_sim_label_1.set_pos(5, 25)
setting_sim_label_1.set_size(103, 20)
setting_sim_label_1.set_text("SIM卡切换")
setting_sim_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_sim_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_sim_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_screen_list = lv.list(setting_sim)
setting_sim_screen_list.set_pos(0, 40)
setting_sim_screen_list.set_size(128, 69)
setting_sim_screen_list.set_style_pad_left(2, 0)
setting_sim_screen_list.set_style_pad_top(4, 0)
setting_sim_screen_list.set_style_pad_row(3, 0)
setting_sim_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_sim_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_sim_cont_bottom = lv.obj(setting_sim)
setting_sim_cont_bottom.set_pos(0, 111)
setting_sim_cont_bottom.set_size(128, 19)
setting_sim_bottom_label = lv.label(setting_sim_cont_bottom)
setting_sim_bottom_label.set_pos(25, 0)
setting_sim_bottom_label.set_size(103, 19)
setting_sim_bottom_label.set_text("")
setting_sim_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_sim_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_sim_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_bottom_img = lv.img(setting_sim_cont_bottom)
setting_sim_bottom_img.set_pos(5, 0)
setting_sim_bottom_img.set_size(15, 16)
setting_sim_bottom_img.set_src('B:/static/menber.png')
setting_sim_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_sim_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# POC平台切换
setting_platform = lv.obj()
setting_platform.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_platform_cont_top = lv.obj(setting_platform)
setting_platform_cont_top.set_pos(0, 0)
setting_platform_cont_top.set_size(128, 20)
setting_platform_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_platform_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_top_battery = lv.img(setting_platform_cont_top)
setting_platform_top_battery.set_pos(109, 5)
setting_platform_top_battery.set_size(16, 13)
setting_platform_top_battery.set_src('B:/static/battery_4.png')
setting_platform_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_top_gps = lv.img(setting_platform_cont_top)
setting_platform_top_gps.set_pos(50, 4)
setting_platform_top_gps.set_size(14, 14)
setting_platform_top_gps.set_src('B:/static/gps.png')
setting_platform_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_top_ej_img = lv.img(setting_platform_cont_top)
setting_platform_top_ej_img.set_pos(93, 5)
setting_platform_top_ej_img.set_size(14, 14)
setting_platform_top_ej_img.set_src('B:/static/earphone1.png')
setting_platform_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_top_sim_id = lv.img(setting_platform_cont_top)
setting_platform_top_sim_id.set_pos(36, 4)
setting_platform_top_sim_id.set_size(14, 14)
setting_platform_top_sim_id.set_src('B:/static/1.png')
setting_platform_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_top_signal = lv.img(setting_platform_cont_top)
setting_platform_top_signal.set_pos(2, 2)
setting_platform_top_signal.set_size(16, 16)
setting_platform_top_signal.set_src('B:/static/signal_5.png')
setting_platform_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_top_net = lv.label(setting_platform_cont_top)
setting_platform_top_net.set_pos(18, 4)
setting_platform_top_net.set_size(20, 11)
setting_platform_top_net.set_text("4G")
setting_platform_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_platform_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_platform_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_label_1 = lv.label(setting_platform)
setting_platform_label_1.set_pos(5, 25)
setting_platform_label_1.set_size(103, 20)
setting_platform_label_1.set_text("POC平台设置")
setting_platform_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_platform_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_platform_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_screen_list = lv.list(setting_platform)
setting_platform_screen_list.set_pos(0, 40)
setting_platform_screen_list.set_size(128, 69)
setting_platform_screen_list.set_style_pad_left(2, 0)
setting_platform_screen_list.set_style_pad_top(4, 0)
setting_platform_screen_list.set_style_pad_row(3, 0)
setting_platform_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_platform_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_platform_cont_bottom = lv.obj(setting_platform)
setting_platform_cont_bottom.set_pos(0, 111)
setting_platform_cont_bottom.set_size(128, 19)
setting_platform_bottom_label = lv.label(setting_platform_cont_bottom)
setting_platform_bottom_label.set_pos(25, 0)
setting_platform_bottom_label.set_size(103, 19)
setting_platform_bottom_label.set_text("")
setting_platform_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_platform_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_platform_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_bottom_img = lv.img(setting_platform_cont_bottom)
setting_platform_bottom_img.set_pos(5, 0)
setting_platform_bottom_img.set_size(15, 16)
setting_platform_bottom_img.set_src('B:/static/menber.png')
setting_platform_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_platform_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 设置ptt提示音
setting_ptt_hint_tone = lv.obj()
setting_ptt_hint_tone.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_ptt_hint_tone_cont_top = lv.obj(setting_ptt_hint_tone)
setting_ptt_hint_tone_cont_top.set_pos(0, 0)
setting_ptt_hint_tone_cont_top.set_size(128, 20)
setting_ptt_hint_tone_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_ptt_hint_tone_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_top_battery = lv.img(setting_ptt_hint_tone_cont_top)
setting_ptt_hint_tone_top_battery.set_pos(109, 5)
setting_ptt_hint_tone_top_battery.set_size(16, 13)
setting_ptt_hint_tone_top_battery.set_src('B:/static/battery_4.png')
setting_ptt_hint_tone_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_top_gps = lv.img(setting_ptt_hint_tone_cont_top)
setting_ptt_hint_tone_top_gps.set_pos(50, 4)
setting_ptt_hint_tone_top_gps.set_size(14, 14)
setting_ptt_hint_tone_top_gps.set_src('B:/static/gps.png')
setting_ptt_hint_tone_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_top_ej_img = lv.img(setting_ptt_hint_tone_cont_top)
setting_ptt_hint_tone_top_ej_img.set_pos(93, 5)
setting_ptt_hint_tone_top_ej_img.set_size(14, 14)
setting_ptt_hint_tone_top_ej_img.set_src('B:/static/earphone1.png')
setting_ptt_hint_tone_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_top_sim_id = lv.img(setting_ptt_hint_tone_cont_top)
setting_ptt_hint_tone_top_sim_id.set_pos(36, 4)
setting_ptt_hint_tone_top_sim_id.set_size(14, 14)
setting_ptt_hint_tone_top_sim_id.set_src('B:/static/1.png')
setting_ptt_hint_tone_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_top_signal = lv.img(setting_ptt_hint_tone_cont_top)
setting_ptt_hint_tone_top_signal.set_pos(2, 2)
setting_ptt_hint_tone_top_signal.set_size(16, 16)
setting_ptt_hint_tone_top_signal.set_src('B:/static/signal_5.png')
setting_ptt_hint_tone_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_top_net = lv.label(setting_ptt_hint_tone_cont_top)
setting_ptt_hint_tone_top_net.set_pos(18, 4)
setting_ptt_hint_tone_top_net.set_size(20, 11)
setting_ptt_hint_tone_top_net.set_text("4G")
setting_ptt_hint_tone_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_ptt_hint_tone_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_ptt_hint_tone_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_label_1 = lv.label(setting_ptt_hint_tone)
setting_ptt_hint_tone_label_1.set_pos(5, 25)
setting_ptt_hint_tone_label_1.set_size(103, 20)
setting_ptt_hint_tone_label_1.set_text("PTT提示音")
setting_ptt_hint_tone_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_ptt_hint_tone_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_ptt_hint_tone_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_screen_list = lv.list(setting_ptt_hint_tone)
setting_ptt_hint_tone_screen_list.set_pos(0, 40)
setting_ptt_hint_tone_screen_list.set_size(128, 69)
setting_ptt_hint_tone_screen_list.set_style_pad_left(2, 0)
setting_ptt_hint_tone_screen_list.set_style_pad_top(4, 0)
setting_ptt_hint_tone_screen_list.set_style_pad_row(3, 0)
setting_ptt_hint_tone_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_ptt_hint_tone_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_ptt_hint_tone_cont_bottom = lv.obj(setting_ptt_hint_tone)
setting_ptt_hint_tone_cont_bottom.set_pos(0, 111)
setting_ptt_hint_tone_cont_bottom.set_size(128, 19)
setting_ptt_hint_tone_bottom_label = lv.label(setting_ptt_hint_tone_cont_bottom)
setting_ptt_hint_tone_bottom_label.set_pos(25, 0)
setting_ptt_hint_tone_bottom_label.set_size(103, 19)
setting_ptt_hint_tone_bottom_label.set_text("")
setting_ptt_hint_tone_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_ptt_hint_tone_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_ptt_hint_tone_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_bottom_img = lv.img(setting_ptt_hint_tone_cont_bottom)
setting_ptt_hint_tone_bottom_img.set_pos(5, 0)
setting_ptt_hint_tone_bottom_img.set_size(15, 16)
setting_ptt_hint_tone_bottom_img.set_src('B:/static/menber.png')
setting_ptt_hint_tone_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_ptt_hint_tone_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 设置按键音
setting_keypad_tone = lv.obj()
setting_keypad_tone.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_keypad_tone_cont_top = lv.obj(setting_keypad_tone)
setting_keypad_tone_cont_top.set_pos(0, 0)
setting_keypad_tone_cont_top.set_size(128, 20)
setting_keypad_tone_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_keypad_tone_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_top_battery = lv.img(setting_keypad_tone_cont_top)
setting_keypad_tone_top_battery.set_pos(109, 5)
setting_keypad_tone_top_battery.set_size(16, 13)
setting_keypad_tone_top_battery.set_src('B:/static/battery_4.png')
setting_keypad_tone_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_top_gps = lv.img(setting_keypad_tone_cont_top)
setting_keypad_tone_top_gps.set_pos(50, 4)
setting_keypad_tone_top_gps.set_size(14, 14)
setting_keypad_tone_top_gps.set_src('B:/static/gps.png')
setting_keypad_tone_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_top_ej_img = lv.img(setting_keypad_tone_cont_top)
setting_keypad_tone_top_ej_img.set_pos(93, 5)
setting_keypad_tone_top_ej_img.set_size(14, 14)
setting_keypad_tone_top_ej_img.set_src('B:/static/earphone1.png')
setting_keypad_tone_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_top_sim_id = lv.img(setting_keypad_tone_cont_top)
setting_keypad_tone_top_sim_id.set_pos(36, 4)
setting_keypad_tone_top_sim_id.set_size(14, 14)
setting_keypad_tone_top_sim_id.set_src('B:/static/1.png')
setting_keypad_tone_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_top_signal = lv.img(setting_keypad_tone_cont_top)
setting_keypad_tone_top_signal.set_pos(2, 2)
setting_keypad_tone_top_signal.set_size(16, 16)
setting_keypad_tone_top_signal.set_src('B:/static/signal_5.png')
setting_keypad_tone_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_top_net = lv.label(setting_keypad_tone_cont_top)
setting_keypad_tone_top_net.set_pos(18, 4)
setting_keypad_tone_top_net.set_size(20, 11)
setting_keypad_tone_top_net.set_text("4G")
setting_keypad_tone_top_net.set_long_mode(lv.label.LONG.WRAP)
setting_keypad_tone_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_keypad_tone_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_label_1 = lv.label(setting_keypad_tone)
setting_keypad_tone_label_1.set_pos(5, 25)
setting_keypad_tone_label_1.set_size(103, 20)
setting_keypad_tone_label_1.set_text("按键音")
setting_keypad_tone_label_1.set_long_mode(lv.label.LONG.WRAP)
setting_keypad_tone_label_1.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
setting_keypad_tone_label_1.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_screen_list = lv.list(setting_keypad_tone)
setting_keypad_tone_screen_list.set_pos(0, 40)
setting_keypad_tone_screen_list.set_size(128, 69)
setting_keypad_tone_screen_list.set_style_pad_left(2, 0)
setting_keypad_tone_screen_list.set_style_pad_top(4, 0)
setting_keypad_tone_screen_list.set_style_pad_row(3, 0)
setting_keypad_tone_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
setting_keypad_tone_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
setting_keypad_tone_cont_bottom = lv.obj(setting_keypad_tone)
setting_keypad_tone_cont_bottom.set_pos(0, 111)
setting_keypad_tone_cont_bottom.set_size(128, 19)
setting_keypad_tone_bottom_label = lv.label(setting_keypad_tone_cont_bottom)
setting_keypad_tone_bottom_label.set_pos(25, 0)
setting_keypad_tone_bottom_label.set_size(103, 19)
setting_keypad_tone_bottom_label.set_text("")
setting_keypad_tone_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
setting_keypad_tone_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
setting_keypad_tone_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_bottom_img = lv.img(setting_keypad_tone_cont_bottom)
setting_keypad_tone_bottom_img.set_pos(5, 0)
setting_keypad_tone_bottom_img.set_size(15, 16)
setting_keypad_tone_bottom_img.set_src('B:/static/menber.png')
setting_keypad_tone_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
setting_keypad_tone_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 定位
lbs = lv.obj()
lbs.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
lbs.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
lbs_img = lv.img(lbs)
lbs_img.set_pos(0, 0)
lbs_img.set_size(128, 128)
lbs_img.set_src("B:/static/index1.png")
lbs_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
lbs_label = lv.label(lbs)
lbs_label.set_pos(25, 60)
lbs_label.set_size(108, 27)
lbs_label.set_text("正在查询定位信息...")
lbs_label.set_long_mode(lv.label.LONG.WRAP)
lbs_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
lbs_label.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 天气
weather = lv.obj()
weather.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
weather.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
weather_cont_top = lv.obj(weather)
weather_cont_top.set_pos(0, 0)
weather_cont_top.set_size(128, 20)
weather_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
weather_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_top_battery = lv.img(weather_cont_top)
weather_top_battery.set_pos(109, 5)
weather_top_battery.set_size(16, 13)
weather_top_battery.set_src('B:/static/battery_4.png')
weather_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_top_gps = lv.img(weather_cont_top)
weather_top_gps.set_pos(50, 4)
weather_top_gps.set_size(14, 14)
weather_top_gps.set_src('B:/static/gps.png')
weather_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_top_ej_img = lv.img(weather_cont_top)
weather_top_ej_img.set_pos(93, 5)
weather_top_ej_img.set_size(14, 14)
weather_top_ej_img.set_src('B:/static/earphone1.png')
weather_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_top_sim_id = lv.img(weather_cont_top)
weather_top_sim_id.set_pos(36, 4)
weather_top_sim_id.set_size(14, 14)
weather_top_sim_id.set_src('B:/static/1.png')
weather_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_top_signal = lv.img(weather_cont_top)
weather_top_signal.set_pos(2, 2)
weather_top_signal.set_size(16, 16)
weather_top_signal.set_src('B:/static/signal_5.png')
weather_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_top_net = lv.label(weather_cont_top)
weather_top_net.set_pos(18, 4)
weather_top_net.set_size(20, 11)
weather_top_net.set_text("4G")
weather_top_net.set_long_mode(lv.label.LONG.WRAP)
weather_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
weather_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_cont = lv.obj(weather)
weather_cont.set_pos(0, 20)
weather_cont.set_size(128, 89)
weather_cont.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_cont.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
weather_label = lv.label(weather_cont)  # 使用者
weather_label.set_pos(29, 10)
weather_label.set_size(100, 20)
weather_label.set_text("")
weather_label.set_long_mode(lv.label.LONG.WRAP)
weather_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
weather_label.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_img = lv.img(weather_cont)
weather_img.set_pos(5, 8)
weather_img.set_size(19, 19)
weather_img.set_pivot(0, 0)
weather_img.set_angle(0)
weather_img.add_flag(lv.obj.FLAG.CLICKABLE)
weather_label.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_label1 = lv.label(weather_cont)  # 使用者
weather_label1.set_pos(29, 39)
weather_label1.set_size(100, 20)
weather_label1.set_text("")
weather_label1.set_long_mode(lv.label.LONG.WRAP)
weather_label1.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
weather_label1.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_img1 = lv.img(weather_cont)
weather_img1.set_pos(5, 36)
weather_img1.set_size(19, 19)
weather_img1.set_pivot(0, 0)
weather_img1.set_angle(0)
weather_img1.add_flag(lv.obj.FLAG.CLICKABLE)
weather_label1.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_label2 = lv.label(weather_cont)  # 使用者
weather_label2.set_pos(29, 67)
weather_label2.set_size(100, 20)
weather_label2.set_text("")
weather_label2.set_long_mode(lv.label.LONG.WRAP)
weather_label2.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
weather_label2.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_img2 = lv.img(weather_cont)
weather_img2.set_pos(5, 65)
weather_img2.set_size(19, 19)
weather_img2.set_pivot(0, 0)
weather_img2.set_angle(0)
weather_img2.add_flag(lv.obj.FLAG.CLICKABLE)
weather_label2.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_cont_bottom = lv.obj(weather)
weather_cont_bottom.set_pos(0, 111)
weather_cont_bottom.set_size(128, 19)
weather_bottom_label = lv.label(weather_cont_bottom)
weather_bottom_label.set_pos(25, 0)
weather_bottom_label.set_size(103, 19)
weather_bottom_label.set_text("")
weather_bottom_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
weather_bottom_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
weather_bottom_label.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_bottom_img = lv.img(weather_cont_bottom)
weather_bottom_img.set_pos(5, 0)
weather_bottom_img.set_size(15, 16)
weather_bottom_img.set_src('B:/static/menber.png')
weather_bottom_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
weather_cont_bottom.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 关于本机
about = lv.obj()
about.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
about.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
about.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
about_cont_top = lv.obj(about)
about_cont_top.set_pos(0, 0)
about_cont_top.set_size(128, 20)
about_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
about_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
about_top_battery = lv.img(about_cont_top)
about_top_battery.set_pos(109, 5)
about_top_battery.set_size(16, 13)
about_top_battery.set_src('B:/static/battery_4.png')
about_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
about_top_gps = lv.img(about_cont_top)
about_top_gps.set_pos(50, 4)
about_top_gps.set_size(14, 14)
about_top_gps.set_src('B:/static/gps.png')
about_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
about_top_ej_img = lv.img(about_cont_top)
about_top_ej_img.set_pos(93, 5)
about_top_ej_img.set_size(14, 14)
about_top_ej_img.set_src('B:/static/earphone1.png')
about_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
about_top_sim_id = lv.img(about_cont_top)
about_top_sim_id.set_pos(36, 4)
about_top_sim_id.set_size(14, 14)
about_top_sim_id.set_src('B:/static/1.png')
about_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
about_top_signal = lv.img(about_cont_top)
about_top_signal.set_pos(2, 2)
about_top_signal.set_size(16, 16)
about_top_signal.set_src('B:/static/signal_5.png')
about_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
about_top_net = lv.label(about_cont_top)
about_top_net.set_pos(18, 4)
about_top_net.set_size(20, 11)
about_top_net.set_text("4G")
about_top_net.set_long_mode(lv.label.LONG.WRAP)
about_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
about_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
about_cont = lv.obj(about)
about_cont.set_pos(0, 20)
about_cont.set_size(128, 108)
about_cont.add_style(style_group_white, lv.PART.MAIN | lv.STATE.DEFAULT)
about_cont.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
about_label_group_title = lv.label(about_cont)
about_label_group_title.set_pos(0, 2)
about_label_group_title.set_size(128, 30)
about_label_group_title.set_text("待机时间:")
about_label_group_title.set_long_mode(lv.label.LONG.WRAP)
about_label_group_title.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
about_label_group_title.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
about_label_group_info = lv.label(about_cont)
about_label_group_info.set_pos(0, 20)
about_label_group_info.set_size(128, 90)
about_label_group_info.set_text("")
about_label_group_info.set_long_mode(lv.label.LONG.WRAP)
about_label_group_info.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
about_label_group_info.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# 写号
std_write = lv.obj()
std_write.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
std_write.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
std_write_cont_top = lv.obj(std_write)
std_write_cont_top.set_pos(0, 0)
std_write_cont_top.set_size(128, 20)
std_write_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
std_write_cont_top.add_style(style_bg, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
std_write_top_battery = lv.img(std_write_cont_top)
std_write_top_battery.set_pos(109, 5)
std_write_top_battery.set_size(16, 13)
std_write_top_battery.set_src('B:/static/battery_4.png')
std_write_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_top_gps = lv.img(std_write_cont_top)
std_write_top_gps.set_pos(50, 4)
std_write_top_gps.set_size(14, 14)
std_write_top_gps.set_src('B:/static/gps.png')
std_write_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_top_ej_img = lv.img(std_write_cont_top)
std_write_top_ej_img.set_pos(93, 5)
std_write_top_ej_img.set_size(14, 14)
std_write_top_ej_img.set_src('B:/static/earphone1.png')
std_write_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_top_sim_id = lv.img(std_write_cont_top)
std_write_top_sim_id.set_pos(36, 4)
std_write_top_sim_id.set_size(14, 14)
std_write_top_sim_id.set_src('B:/static/1.png')
std_write_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_top_signal = lv.img(std_write_cont_top)
std_write_top_signal.set_pos(2, 2)
std_write_top_signal.set_size(16, 16)
std_write_top_signal.set_src('B:/static/signal_5.png')
std_write_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_top_net = lv.label(std_write_cont_top)
std_write_top_net.set_pos(18, 4)
std_write_top_net.set_size(20, 11)
std_write_top_net.set_text("4G")
std_write_top_net.set_long_mode(lv.label.LONG.WRAP)
std_write_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
std_write_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_cont = lv.obj(std_write)
std_write_cont.set_pos(0, 20)
std_write_cont.set_size(128, 108)
std_write_cont.add_style(style_group_white, lv.PART.MAIN | lv.STATE.DEFAULT)
std_write_cont.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
std_write_label1 = lv.label(std_write_cont)  # 使用者
std_write_label1.set_pos(0, 0)
std_write_label1.set_size(128, 60)
std_write_label1.set_text("写号模式,等待写号中")
std_write_label1.set_long_mode(lv.label.LONG.WRAP)
std_write_label1.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
std_write_label1.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
# ####################################################################### qr_code 页面 #
qr_code_bg_color = lv.color_make(0xff, 0xff, 0xff)
qr_code_fg_color = lv.color_make(0x00, 0x00, 0x00)
# ####################################################################### nodify 页面 #
notify = lv.obj()
notify.add_style(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)
notify.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
notify.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
notify_cont_top = lv.obj(notify)
notify_cont_top.set_pos(0, 0)
notify_cont_top.set_size(128, 20)
notify_cont_top.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
notify_cont_top.add_style(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_top_battery = lv.img(notify_cont_top)
notify_top_battery.set_pos(109, 5)
notify_top_battery.set_size(16, 13)
notify_top_battery.set_src('B:/static/battery_4.png')
notify_top_battery.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_top_gps = lv.img(notify_cont_top)
notify_top_gps.set_pos(50, 4)
notify_top_gps.set_size(14, 14)
notify_top_gps.set_src('B:/static/gps.png')
notify_top_gps.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_top_ej_img = lv.img(notify_cont_top)
notify_top_ej_img.set_pos(93, 5)
notify_top_ej_img.set_size(14, 14)
notify_top_ej_img.set_src('B:/static/earphone1.png')
notify_top_ej_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_top_sim_id = lv.img(notify_cont_top)
notify_top_sim_id.set_pos(36, 4)
notify_top_sim_id.set_size(14, 14)
notify_top_sim_id.set_src('B:/static/1.png')
notify_top_sim_id.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_top_signal = lv.img(notify_cont_top)
notify_top_signal.set_pos(2, 2)
notify_top_signal.set_size(16, 16)
notify_top_signal.set_src('B:/static/signal_5.png')
notify_top_signal.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_top_net = lv.label(notify_cont_top)
notify_top_net.set_pos(18, 4)
notify_top_net.set_size(20, 11)
notify_top_net.set_text("4G")
notify_top_net.set_long_mode(lv.label.LONG.WRAP)
notify_top_net.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
notify_top_net.add_style(style_siyuan_white_14, lv.PART.MAIN | lv.STATE.DEFAULT)

notify_cont = lv.img(notify)
notify_cont.set_pos(0, 20)
notify_cont.set_size(128, 88)
notify_cont.add_style(style_group_white, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_cont.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)

notify_footer_label_imei = lv.label(notify)
notify_footer_label_imei.set_pos(0, 95)
notify_footer_label_imei.set_size(128, 14)
notify_footer_label_imei.set_long_mode(lv.label.LONG.WRAP)
notify_footer_label_imei.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
notify_footer_label_imei.add_style(style_siyuan_11_black, lv.PART.MAIN | lv.STATE.DEFAULT)
notify_footer_label_popup_label = lv.label(notify)
notify_footer_label_popup_label.set_pos(0, 108)
notify_footer_label_popup_label.set_size(128, 20)
notify_footer_label_popup_label.set_text("无SIM卡!")
notify_footer_label_popup_label.set_long_mode(lv.label.LONG.WRAP)
notify_footer_label_popup_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
notify_footer_label_popup_cont = lv.style_t()
notify_footer_label_popup_cont.init()
notify_footer_label_popup_cont.set_radius(0)
notify_footer_label_popup_cont.set_bg_color(lv.color_make(0xe2, 0xdc, 0x22))
notify_footer_label_popup_cont.set_bg_grad_color(lv.color_make(0xf6, 0xda, 0x23))
notify_footer_label_popup_cont.set_bg_grad_dir(lv.GRAD_DIR.VER)
notify_footer_label_popup_cont.set_bg_opa(255)
notify_footer_label_popup_cont.set_text_color(lv.color_make(0x00, 0x00, 0x00))
notify_footer_label_popup_cont.set_text_font(lv.ali_14_font)
notify_footer_label_popup_cont.set_text_letter_space(2)
notify_footer_label_popup_cont.set_pad_left(0)
notify_footer_label_popup_cont.set_pad_right(0)
notify_footer_label_popup_cont.set_pad_top(0)
notify_footer_label_popup_cont.set_pad_bottom(0)
notify_footer_label_popup_label.add_style(notify_footer_label_popup_cont, lv.PART.MAIN | lv.STATE.DEFAULT)


class Screen(Abstract):
    def __init__(self):
        self.load_status = True
        self.meta = None

    def post_processor_after_load(self):
        pass

    def set_meta(self, msg):
        self.meta = msg

    def load_start(self):
        self.load_status = False

    def load_end(self):
        self.load_status = True

    def up_long_press(self):
        pass

    def get_load(self):
        return self.load_status

    def deactivate(self):
        pass

    @staticmethod
    def publish_ope():
        # 主动向后端请求运营商资源
        return EventMesh.publish("screen_get_ope")

    @staticmethod
    def publish_sig():
        # 主动向后端请求信号强度
        return EventMesh.publish("screen_get_sig")

    @staticmethod
    def publish_time():
        # 主动向后端请求时间
        return EventMesh.publish("screen_get_time")

    @staticmethod
    def publish_date():
        # 主动向后端请求时间
        return EventMesh.publish("main_get_date")

    @staticmethod
    def publish_battery():
        # 主动向后端请求电池电量
        return EventMesh.publish("screen_get_battery")


class QrCodeMsgBox(Abstract):

    def __init__(self):
        super().__init__()
        self.qr = None
        self.lock = Lock()

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("qr_code_show", self.show)
        EventMesh.subscribe("qr_code_hide", self.hide)

    def hide(self, event=None, msg=None):
        with self.lock:
            if self.qr is not None:
                self.qr.delete()
                self.qr = None

    def show(self, event=None, msg=None):
        if msg is None:
            msg = dict()
        with self.lock:
            print("---------------show--------------------{}".format(self.qr))
            if self.qr is None:
                self.qr = lv.qrcode(lv.scr_act(), 65, qr_code_fg_color, qr_code_bg_color)
                # Set data
                imei = modem.getDevImei()
                self.qr.set_align(lv.ALIGN.TOP_MID)
                qr_pos = msg.get("pos")
                if qr_pos:
                    self.qr.set_pos(*qr_pos)
                else:
                    self.qr.set_pos(0, 53)
                self.qr.update(imei, len(imei))
                # Add a border with bg_color
                self.qr.set_style_border_color(qr_code_bg_color, 0)
                self.qr.set_style_border_width(5, 0)


class VolMsgBox(object):
    def __init__(self):
        self.vol_box = None
        self.label1 = None
        self.bar1 = None
        self.vol_box_timer = osTimer()

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("msg_box_vol_add", self.add)
        EventMesh.subscribe("msg_box_vol_reduce", self.reduce)
        EventMesh.subscribe("msg_box_vol_show", self.show)

    def add(self, topic, screen):
        vol = EventMesh.publish("screen_vol_add")
        EventMesh.publish("msg_box_vol_show", [screen, vol])

    def reduce(self, topic, screen):
        vol = EventMesh.publish("screen_vol_reduce")
        EventMesh.publish("msg_box_vol_show", [screen, vol])

    def hide(self, *args):
        self.vol_box.delete()
        self.vol_box = None

    def show(self, topic, data):
        if self.vol_box is None:
            self.vol_box_timer.start(2000, 0, self.hide)
            self.vol_box = lv.msgbox(data[0], "", "", [], False)
            self.vol_box.set_size(110, 68)
            self.vol_box.center()
            self.label1 = lv.label(self.vol_box)
            self.label1.set_pos(0, 0)
            self.label1.set_size(90, 12)
            self.label1.add_style(style_siyuan_14_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.label1.set_text("当前音量: " + str(data[1]))
            self.bar1 = lv.bar(self.vol_box)
            self.bar1.set_size(85, 10)
            self.bar1.set_pos(2, 5)
            self.bar1.set_range(0, 11)
            self.bar1.set_value(data[1], 11)
        else:
            self.vol_box_timer.stop()
            self.vol_box_timer.start(2000, 0, self.hide)
            self.label1.set_text("当前音量: " + str(data[1]))
            self.bar1.set_value(data[1], 11)


class KeyLockBox(object):
    '''
    键盘锁标识
    '''

    def __init__(self):
        super().__init__()
        self.top_lock_img = None
        self.lock = Lock()

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("top_lock_img_show", self.top_lock_img_show)
        EventMesh.subscribe("top_lock_img_hide", self.top_lock_img_hide)

    def top_lock_img_hide(self, event=None, msg=None):
        with self.lock:
            if self.top_lock_img is not None:
                self.top_lock_img.delete()
                self.top_lock_img = None

    def top_lock_img_show(self, event=None, msg=None):
        with self.lock:
            if self.top_lock_img is None:
                self.top_lock_img = lv.img(main_screen)
                self.top_lock_img.set_pos(79, 5)
                self.top_lock_img.set_size(14, 14)
                self.top_lock_img.set_src('B:/static/lock.png')
                self.top_lock_img.set_pivot(0, 0)
                self.top_lock_img.set_angle(0)
                self.top_lock_img.add_flag(lv.obj.FLAG.CLICKABLE)
                self.top_lock_img.add_style(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)


class PopupMsgBox(object):
    '''设置结果弹窗'''

    def __init__(self):
        super().__init__()
        self.opoup_window_box = None
        self.opoup_window_label = None
        self.opoup_window_box = None

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("msg_box_popup_show", self.show)

    def show(self, topic, data):
        screen_obj = data.get("screen")
        show_msg = data.get("msg")
        font_style = data.get("font")
        sleep_time = data.get("sleep_time", 1)
        self.opoup_window_box = lv.msgbox(screen_obj, "", "", [], False)
        self.opoup_window_box.set_size(100, 55)
        self.opoup_window_box.center()
        self.opoup_window_label = lv.label(self.opoup_window_box)
        self.opoup_window_label.set_pos(0, 0)
        self.opoup_window_label.set_size(66, 12)
        self.opoup_window_label.add_style(font_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.opoup_window_label.set_text(show_msg)
        self.opoup_window_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        utime.sleep(sleep_time)
        self.opoup_window_box.delete()


class MainScreen(Screen):
    NAME = "main"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 6
        self.usr_name = None
        self.lock_key_state = False
        self.comp = main_screen
        self.main_top_img_battery = main_top_battery
        self.main_top_img_gps = main_top_gps
        self.main_top_gps = main_top_gps
        self.main_top_img_group_id = main_top_sim_id
        self.main_top_img_signal = main_top_signal
        self.main_top_img_ej = main_top_ej_img
        self.operator_label = main_operator_label
        self.member_label = main_member_label
        self.user_id_label = main_user_id_label
        self.weather_label = main_weather_label
        self.main_weather_img = main_weather_img
        self.main_top_net = main_top_net
        self.main_bottom_time_label = main_bottom_time_label
        self.main_bottom_date_label = main_bottom_date_label

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("main_group_cur", self.main_group_cur_cb)
        EventMesh.subscribe("switch_btn_ok_show", self.__switch_btn_ok_show)
        EventMesh.subscribe("update_session_info", self.__update_session_info)
        EventMesh.subscribe("update_weather", self.update_weather)
        EventMesh.subscribe("clear_user_btn_style", self.clear_user_btn_style)
        EventMesh.subscribe("add_user_btn_style", self.add_user_btn_style)

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("time", self.__time_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.main_top_gps.set_src('gps.png')
        else:
            self.main_top_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.main_top_net.set_text(msg)

    def post_processor_after_load(self):
        # 获取用户
        self.__load_user()
        # 获取当前组群
        self.__load_group_cur()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        signal = self.publish_sig()
        if signal:
            self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        if battery:
            self.__battery_cb(None, battery)
        # 获取运营商
        ope = self.publish_ope()
        if ope:
            self.__ope_show(None, ope)
        # 获取时间
        time = self.publish_time()
        if time:
            self.__time_cb(None, time)
        self.__load_sim_id()
        EventMesh.publish("request_weather_info")
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)

    def initialization(self):
        self.load_start()
        # 获取信号强度
        self.load_end()

    def get_comp(self):
        return self.comp

    def ok(self):
        # 待机页面 ok 跳转 菜单
        EventMesh.publish("load_screen", {"screen": "menu", "init": True})

    def back(self):
        """优先退出群组判断"""
        return EventMesh.publish("exit_call_member") == -1

    def down(self):
        EventMesh.publish("msg_box_vol_reduce", self.comp)

    def up(self):
        EventMesh.publish("msg_box_vol_add", self.comp)

    def __load_main_bottom(self):
        self.menu_cont_bottom.delete()

    def __switch_btn_ok_show(self, topic, mode):
        if mode:
            self.lock_key_state = True
            main_bottom_date_label.set_text("解锁")
        else:
            self.lock_key_state = False
            self.__time_cb(None, self.publish_time())

    def __update_session_info(self, topic, msg):
        self.user_id_label.set_text(msg)

    def __load_user(self):
        dev_usr = EventMesh.publish("about_get_user")
        self.usr_name = dev_usr
        self.user_id_label.set_text(dev_usr + "(空闲)")
        return dev_usr

    def update_weather(self, topic=None, data=None):
        if data:
            weather_msg = data[0][0][0] + "  " + data[0][1]
            img_path = data[0][0][1]
            self.main_weather_img.set_src(img_path)
            self.weather_label.set_text(weather_msg)

    def add_user_btn_style(self, topic=None, mode=None):
        if mode:
            self.user_id_label.set_style_bg_color(lv.color_make(0xdc, 0x1e, 0x1e), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.user_id_label.set_style_bg_grad_color(lv.color_make(0xdc, 0x1e, 0x1e), lv.PART.MAIN | lv.STATE.DEFAULT)
        else:
            self.user_id_label.set_style_bg_color(lv.color_make(0x28, 0x3d, 0xe2), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.user_id_label.set_style_bg_grad_color(lv.color_make(0x28, 0x3d, 0xe2), lv.PART.MAIN | lv.STATE.DEFAULT)

    def clear_user_btn_style(self, topic=None, mode=None):
        self.user_id_label.set_style_bg_color(lv.color_make(0x00, 0x00, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.user_id_label.set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.main_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.main_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.member_label.set_text(ret)

    def __battery_cb(self, topic, battery):
        self.main_top_img_battery.set_src(battery)

    def __time_cb(self, topic, time):
        self.main_bottom_time_label.set_text(time[1])
        if not self.lock_key_state:
            self.main_bottom_date_label.set_text(time[0])

    def __ope_show(self, topic, ope):
        self.operator_label.set_text(ope)

    def main_group_cur_cb(self, topic, group):
        self.member_label.set_text(group)

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.main_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.main_top_img_group_id.set_src('B:/static/1.png')

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.main_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.main_top_img_signal.set_src('B:/static/signal_0.png')


class NotifyScreen(Screen):
    NAME = "notify"

    def __init__(self):
        super().__init__()
        self.comp = notify
        self.notify_top_img_battery = notify_top_battery
        self.notify_top_img_gps = notify_top_gps
        self.notify_top_img_group_id = notify_top_sim_id
        self.notify_top_img_signal = notify_top_signal
        self.notify_top_img_ej = notify_top_ej_img
        self.notify_top_net = notify_top_net
        self.notify_top_gps = notify_top_gps
        self.notify_footer_label_imei = notify_footer_label_imei
        self.notify_footer_label_popup_label = notify_footer_label_popup_label
        self.notify_cont = notify_cont

    def post_processor_before_initialization(self):
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.notify_top_gps.set_src('gps.png')
        else:
            self.notify_top_gps.set_src('B:/static/gps.png')

    def up_long_press(self):
        print("notify --- up_long_press ----")
        EventMesh.publish("load_screen", {"screen": "setting_platform", "init": True, "back": {"screen": "notify"}})

    def __net_cb(self, event, msg):
        self.notify_top_net.set_text(msg)

    def get_comp(self):
        return self.comp

    def initialization(self):
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        if self.meta.get("reason"):
            self.notify_footer_label_popup_label.set_text(self.meta.get("reason"))
        self.__load_sim_id()

    def post_processor_after_load(self):
        if not EventMesh.publish("persistent_config_get", "platform"):
            self.notify_cont.set_src("")
            self.notify_footer_label_imei.set_text(modem.getDevImei())
            EventMesh.publish("qr_code_show", {"pos": (0, 20)})
        else:
            self.notify_footer_label_imei.set_text("")
            self.notify_cont.set_src("B:/static/index.png")

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.notify_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.notify_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.notify_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.notify_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.notify_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.notify_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.notify_top_img_group_id.set_src('B:/static/1.png')

    def ok(self):
        EventMesh.publish("load_screen", {"screen": "setting_sim", "init": True, "back": {"screen": "notify"}})

    def down(self):
        pass

    def up(self):
        pass

    def back(self):
        pass

    def deactivate(self):
        print("deactivate ~~~")
        EventMesh.publish("qr_code_hide")


class MenuScreen(Screen):
    NAME = "menu"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 6
        self.comp = menu_screen
        self.menu_screen_btn = menu_screen_btn
        self.menu_screen_btn1 = menu_screen_btn1
        self.menu_screen_btn2 = menu_screen_btn2
        self.menu_screen_btn3 = menu_screen_btn3
        self.menu_screen_btn4 = menu_screen_btn4
        self.menu_screen_btn5 = menu_screen_btn5
        self.menu_top_img_battery = menu_top_battery
        self.menu_top_img_group_id = menu_top_sim_id
        self.menu_top_img_signal = menu_top_signal
        self.menu_top_img_ej = menu_top_ej_img
        self.menu_bottom_label = menu_bottom_label
        self.menu_top_net = menu_top_net
        self.menu_top_gps = menu_top_gps
        self.menu_ui_btn_dict = {
            0: self.menu_screen_btn,
            1: self.menu_screen_btn1,
            2: self.menu_screen_btn2,
            3: self.menu_screen_btn3,
            4: self.menu_screen_btn4,
            5: self.menu_screen_btn5
        }

    def post_processor_before_initialization(self):
        EventMesh.subscribe("group_cur", self.main_group_cur_cb)
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.menu_top_gps.set_src('gps.png')
        else:
            self.menu_top_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.menu_top_net.set_text(msg)

    def post_processor_after_load(self):
        # 获取信号强度
        self.__signal_cb(None, self.publish_sig())
        # 获取电池电量
        self.__battery_cb(None, self.publish_battery())
        self.__load_group_cur()
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def initialization(self):
        self.load_start()
        if self.meta.get("init"):
            if self.cur >= 0:
                self.__clear_menu_state()
            self.cur = 0
            self.__add_menu_state()
        self.load_end()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")

    def get_comp(self):
        return self.comp

    def ok(self):
        if self.cur == 0:
            EventMesh.publish("load_screen", {"screen": "group", "init": True})
        elif self.cur == 1:
            EventMesh.publish("load_screen", {"screen": "member", "init": True})
        elif self.cur == 2:
            EventMesh.publish("load_screen", {"screen": "weather", "init": True})
        elif self.cur == 3:
            EventMesh.publish("load_screen", {"screen": "location", "init": True})
        elif self.cur == 4:
            EventMesh.publish("load_screen", {"screen": "setting", "init": True})
        elif self.cur == 5:
            EventMesh.publish("load_screen", {"screen": "about", "init": True})

    def back(self):
        if self.cur > 0:
            self.__clear_menu_state()
        EventMesh.publish("load_screen", {"screen": "main", "init": True, "back": {"screen": "main"}})

    def down(self):
        cur = self.cur + 1
        self.__clear_menu_state()
        if cur > self.count - 1:
            cur = 0
            self.cur = cur
        else:
            self.cur = cur
        self.__add_menu_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_menu_state()
        if cur < 0:
            cur = self.count - 1
            self.cur = cur
        else:
            self.cur = cur
        self.__add_menu_state()

    def __clear_menu_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if self.menu_ui_btn_dict.get(cur):
            self.menu_ui_btn_dict.get(cur).set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
            self.menu_ui_btn_dict.get(cur).set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                   lv.PART.MAIN | lv.STATE.DEFAULT)
            self.menu_ui_btn_dict.get(cur).scroll_to_view(lv.ANIM.OFF)

    def __add_menu_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.menu_ui_btn_dict.get(cur).set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                          lv.PART.MAIN | lv.STATE.DEFAULT)
        self.menu_ui_btn_dict.get(cur).set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                               lv.PART.MAIN | lv.STATE.DEFAULT)
        self.menu_ui_btn_dict.get(cur).scroll_to_view(lv.ANIM.OFF)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.menu_bottom_label.set_text(ret)

    def __battery_cb(self, topic, battery):
        self.menu_top_img_battery.set_src(battery)

    def main_group_cur_cb(self, topic, group):
        self.menu_bottom_label.set_text(group)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.menu_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.menu_top_img_signal.set_src('B:/static/signal_0.png')

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.menu_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.menu_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.menu_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.menu_top_img_group_id.set_src('B:/static/1.png')


class GroupScreen(Screen):
    NAME = "group"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 6
        self.current_button = None
        self.comp = group
        self.group_list = list()
        self.group_top_img_battery = group_top_battery
        self.group_top_img_group_id = group_top_sim_id
        self.group_top_img_signal = group_top_signal
        self.group_top_img_ej = group_top_ej_img
        self.group_bottom_label = group_bottom_label
        self.group_top_net = group_top_net
        self.group_top_gps = group_top_gps
        self.group_bottom_name = None
        self.group_screen_list = group_screen_list
        self.group_btn_list = []
        self.group_update_flag = True

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("update_group_info", self.update_group_info)

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.group_top_gps.set_src('gps.png')
        else:
            self.group_top_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.group_top_net.set_text(msg)

    def post_processor_after_load(self):
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)

    def update_group_info(self, event, mode):
        # 更新群组
        self.group_update_flag = True

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        self.__load_group_list()
        if self.group_list is None or self.group_list == -1 or not len(self.group_list):
            EventMesh.publish("global_popup_window", {"msg": "不在组"})
            return False
        self.__group_screen_list_create()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        if self.cur >= 0:
            self.__clear_group_state()
        self.cur = 0
        self.__add_group_state()
        self.load_end()
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        EventMesh.publish("group_enterbtn_click", self.cur)
        EventMesh.publish("load_screen", {"screen": "main", "init": True})
        # EventMesh.publish("update_member_state")
        # self.group_update_flag = True

    def back(self):
        EventMesh.publish("load_screen", {"screen": "menu"})

    def down(self):
        cur = self.cur + 1
        self.__clear_group_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_group_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_group_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_group_state()

    def __clear_group_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if self.currentButton:
            self.currentButton = self.group_screen_list.get_child(cur)
            self.currentButton.set_style_bg_color(lv.color_make(0x00, 0x00, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_group_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.group_screen_list.get_child(cur)
        self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.group_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.group_top_img_signal.set_src('B:/static/signal_0.png')

    def group_cur_cb(self, topic, group):
        self.group_bottom_label.set_text(group)
        self.group_bottom_name = group

    def __battery_cb(self, topic, battery):
        self.group_top_img_battery.set_src(battery)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.group_bottom_name = ret
            self.group_bottom_label.set_text(ret)

    def __load_group_list(self):
        if not self.group_update_flag:
            return
        response = EventMesh.publish("group_get_list")
        # 判断是否获取到组群列表
        if response:
            self.count, self.group_list = response

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.group_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.group_top_img_ej.set_src('B:/static/earphone1.png')

    def clear_checked_btn(self):
        for i in range(self.count):
            self.__clear_group_state(i)

    def __group_screen_list_create(self):
        """组群界面列表重新创建"""
        # 把之前的list删掉
        if self.group_update_flag:
            self.group_screen_list.delete()
            # 再创建list
            self.group_screen_list = lv.list(self.comp)
            self.group_screen_list.set_pos(0, 20)
            self.group_screen_list.set_size(128, 87)
            self.group_screen_list.set_style_pad_left(2, 0)
            self.group_screen_list.set_style_pad_top(4, 0)
            self.group_screen_list.set_style_pad_row(3, 0)
            self.group_screen_list.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.group_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.group_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的group列表往group_screen_list
                self.add_group_msg(0, self.count)
                self.currentButton = self.group_screen_list.get_child(0)
                self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
                self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                           lv.PART.MAIN | lv.STATE.DEFAULT)
                self.currentButton.scroll_to_view(lv.ANIM.OFF)
                self.group_update_flag = False
            else:
                # TODO:无组群信息弹窗提示
                print("未搜到组群")

    def add_group_msg(self, index, end):
        self.group_btn_list = []
        for each in self.group_list[index:end]:
            _group_btn = lv.btn(self.group_screen_list)
            _group_btn.set_pos(20, 0)
            _group_btn.set_size(128, 18)
            _group_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            btn_img = lv.img(_group_btn)
            btn_img.set_pos(0, 0)
            btn_img.set_size(17, 18)
            btn_img.set_src('B:/static/menber.png')
            group_label = lv.label(_group_btn)
            group_label.set_pos(25, 1)
            group_label.set_size(105, 18)
            group_label.set_text(each[1])
            group_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
            group_label.add_style(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.group_btn_list.append(_group_btn)

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.group_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.group_top_img_group_id.set_src('B:/static/1.png')


class MemberScreen(Screen):
    NAME = "member"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 6
        self.currentButton = None
        self.comp = member
        self.member_top_img_battery = member_top_battery
        self.member_top_img_group_id = member_top_sim_id
        self.member_top_img_signal = member_top_signal
        self.member_top_img_ej = member_top_ej_img
        self.member_bottom_label = member_bottom_label
        self.member_bottom_name = None
        self.member_screen_list = member_screen_list
        self.member_top_net = member_top_net
        self.member_top_gps = member_top_gps
        self.member_list = list()
        self.member_btn_list = list()
        self.member_check_cur_list = list()
        self.member_update_flag = True

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("get_member_check_list", self.__get_member_check_list)
        EventMesh.subscribe("send_select_member_list", self.__send_select_member_list)
        EventMesh.subscribe("update_member_info", self.update_member_info)

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.member_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.member_top_gps.set_src('gps.png')
        else:
            self.member_top_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.member_top_net.set_text(msg)

    def post_processor_after_load(self):
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)

    def update_member_info(self, event, mode):
        self.member_update_flag = True

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        self.__load_member_list()
        if self.member_list is None or self.member_list == -1 or not len(self.member_list):
            EventMesh.publish("global_popup_window", {"msg": "无成员"})
            return False
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        self.__member_screen_list_create()
        if self.cur >= 0:
            self.__clear_member_state()
        self.cur = 0
        self.__add_member_state()
        self.load_end()
        # 获取信号强度
        self.__signal_cb(None, self.publish_sig())
        # 获取电池电量
        self.__battery_cb(None, self.publish_battery())
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def __get_member_check_list(self, topic=None, mode=None):
        if self.member_check_cur_list:
            return True
        else:
            return False

    def __send_select_member_list(self, topic=None, mode=None):
        self.cur = 0
        self.member_update_flag = True
        send_list = []
        for i in self.member_check_cur_list:
            send_list.append(self.member_list[i][0])
        EventMesh.publish("member_speakbtn_click", send_list)
        EventMesh.publish("load_screen", {"screen": "main", "init": True})
        self.__clear_member_img_state()

    def ok(self):
        self.__update_check_img_state(self.cur)

    def back(self):
        self.__clear_member_img_state()
        EventMesh.publish("load_screen", {"screen": "menu"})

    def down(self):
        cur = self.cur + 1
        self.__clear_member_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_member_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_member_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_member_state()

    def clear_checked_btn(self):
        for i in range(self.count):
            self.__clear_member_state(i)

    def __clear_member_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.member_btn_list):
            self.currentButton = self.member_screen_list.get_child(cur)
            self.member_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                            lv.PART.MAIN | lv.STATE.DEFAULT)
            self.member_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_member_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.member_screen_list.get_child(cur)
        self.member_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                        lv.PART.MAIN | lv.STATE.DEFAULT)
        self.member_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __update_check_img_state(self, cur=None):
        if cur is None:
            cur = self.cur
        member_state = self.member_list[cur][2]
        if member_state == 2:
            return
        if self.member_check_cur_list:
            if cur in self.member_check_cur_list:
                self.member_check_cur_list.remove(cur)
                if member_state == 1:
                    img_path_name = "B:/static/member_online.png"
                else:
                    img_path_name = "B:/static/member_onlines.png"
            else:
                self.member_check_cur_list.append(cur)
                if member_state == 1:
                    img_path_name = "B:/static/member_check.png"
                else:
                    img_path_name = "B:/static/member_checks.png"
        else:
            self.member_check_cur_list.append(cur)
            if member_state == 1:
                img_path_name = "B:/static/member_check.png"
            else:
                img_path_name = "B:/static/member_checks.png"
        self.member_btn_list[cur][0].set_src(img_path_name)

    def __clear_member_img_state(self):
        if self.member_check_cur_list:
            for i in self.member_check_cur_list:
                member_state = self.member_list[i][2]
                if member_state == 1:
                    img_path_name = "B:/static/member_online.png"
                else:
                    img_path_name = "B:/static/member_onlines.png"
                self.member_btn_list[i][0].set_src(img_path_name)
            self.member_check_cur_list = []

    def __load_member_list(self):
        if not self.member_update_flag:
            return
        else:
            response = EventMesh.publish("member_get_list")
            if response:
                self.count, self.member_list = response

    def __member_screen_list_create(self):
        """成员界面列表重新创建"""
        # 把之前的list删掉
        if self.member_update_flag:
            self.member_screen_list.delete()
            # 再创建list
            self.member_screen_list = lv.list(self.comp)
            self.member_screen_list.set_pos(0, 21)
            self.member_screen_list.set_size(128, 87)
            self.member_screen_list.set_style_pad_left(2, 0)
            self.member_screen_list.set_style_pad_top(1, 0)
            self.member_screen_list.set_style_pad_row(4, 0)
            self.member_screen_list.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.member_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.member_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                self.add_member_msg(0, self.count)
                self.currentButton = self.member_screen_list.get_child(0)
                self.member_btn_list[0][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
                self.member_btn_list[0][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                   lv.PART.MAIN | lv.STATE.DEFAULT)
                self.currentButton.scroll_to_view(lv.ANIM.OFF)
                self.member_update_flag = False
            else:
                # TODO:无成员信息弹窗提示
                print("未搜到成员")
                pass

    def add_member_msg(self, index, end):
        self.member_btn_list = []
        for each in self.member_list[index:end]:
            member_btn = lv.btn(self.member_screen_list)
            member_btn.set_pos(20, 0)
            member_btn.set_size(128, 18)
            member_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            btn_img = lv.img(member_btn)
            btn_img.set_pos(2, 0)
            btn_img.set_size(17, 17)
            if each[2] == 1:
                img_path = 'B:/static/member_online.png'
            elif each[2] == 3:
                img_path = 'B:/static/member_onlines.png'
            elif each[2] == 2:
                img_path = 'B:/static/member_offline.png'
            else:
                img_path = 'B:/static/member_offline.png'
            btn_img.set_src(img_path)
            member_label = lv.label(member_btn)
            member_label.set_pos(20, 1)
            member_label.set_size(106, 18)
            member_label.set_text(each[1])
            member_label.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
            member_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.member_btn_list.append((btn_img, member_label, member_btn))

    def member_group_cur_cb(self, topic, group):
        self.member_bottom_label.set_text(group)
        self.member_bottom_name = group

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.member_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.member_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.member_top_img_battery.set_src(battery)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.member_bottom_label.set_text(ret)
            self.member_bottom_name = ret

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.member_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.member_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.member_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.member_top_img_group_id.set_src('B:/static/1.png')

    # def update_member_state(self, topic=None, mode=None):
    #     self.member_update_flag = True


class SettingScreen(Screen):
    NAME = "setting"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 7
        self.comp = setting
        self.currentButton = None
        self.setting_label_list = list()
        self.setting_screen_list = setting_screen_list
        self.setting_top_img_battery = setting_top_battery
        self.setting_top_img_group_id = setting_top_sim_id
        self.setting_top_img_signal = setting_top_signal
        self.setting_top_img_ej = setting_top_ej_img
        self.setting_bottom_label = setting_bottom_label
        self.setting_update_flag = True
        self.setting_top_net = setting_top_net
        self.setting_top_gps = setting_top_gps
        self.setting_screen_property = [
            "PTT提示音",
            "按键音",
            "息屏时间",
            "单呼退出时间",
            "省电管理",
            "SIM卡切换",
            "POC平台切换",
        ]

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.setting_top_gps.set_src('gps.png')
        else:
            self.setting_top_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.setting_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        if self.cur >= 0:
            self.__clear_setting_state()
        if self.meta.get('init'):
            self.cur = 0
            mode = 1
        else:
            mode = 0
        self.__setting_screen_list_create(mode)
        self.__add_setting_state()
        self.load_end()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        # 获取信号强度
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        if self.cur == 0:
            EventMesh.publish("load_screen", {"screen": "setting_ptt_hint_tone", "init": True})
        elif self.cur == 1:
            EventMesh.publish("load_screen", {"screen": "setting_keypad_tone", "init": True})
        elif self.cur == 2:
            EventMesh.publish("load_screen", {"screen": "setting_sleep", "init": True})
        elif self.cur == 3:
            EventMesh.publish("load_screen", {"screen": "setting_call_time", "init": True})
        elif self.cur == 4:
            EventMesh.publish("load_screen", {"screen": "setting_battery", "init": True})
        elif self.cur == 5:
            EventMesh.publish("load_screen", {"screen": "setting_sim", "init": True})
        elif self.cur == 6:
            EventMesh.publish("load_screen", {"screen": "setting_platform", "init": True})

    def back(self):
        EventMesh.publish("load_screen", {"screen": "menu"})

    def down(self):
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __setting_screen_list_create(self, mode):
        """成员界面列表重新创建"""
        # 把之前的list删掉
        if self.setting_update_flag:
            self.setting_screen_list.delete()
            if self.setting_label_list:
                self.setting_label_list = []
            # 再创建list
            self.setting_screen_list = lv.list(self.comp)
            self.setting_screen_list.set_pos(0, 20)
            self.setting_screen_list.set_size(128, 89)
            self.setting_screen_list.set_style_pad_left(2, 0)
            self.setting_screen_list.set_style_pad_top(4, 0)
            self.setting_screen_list.set_style_pad_row(3, 0)
            self.setting_screen_list.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.setting_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.setting_screen_list)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = "B:/static/number_{}.png".format(str(num + 1))
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(20, 0)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_label_list.append((setting_btn, setting_label, setting_btn_img))
                self.setting_update_flag = False
                if mode:
                    self.currentButton = self.setting_screen_list.get_child(0)
                    self.setting_label_list[0][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                     lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_label_list[0][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                          lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_label_list):
            self.setting_label_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                               lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_label_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                    lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.setting_screen_list.get_child(cur)
        self.setting_label_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                           lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_label_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_group_cur_cb(self, topic, group):
        self.setting_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.setting_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.setting_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.setting_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.setting_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.setting_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.setting_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.setting_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.setting_top_img_group_id.set_src('B:/static/1.png')


class SettingSleepScreen(Screen):
    NAME = "setting_sleep"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 9
        self.comp = setting_rest_screen
        self.currentButton = None
        self.check_state_cur = None
        self.sleep_setting_list_1 = setting_rest_screen_screen_list
        self.sleep_setting_top_img_battery = setting_rest_top_battery
        self.sleep_setting_top_img_group_id = setting_rest_top_sim_id
        self.sleep_setting_top_img_signal = setting_rest_top_signal
        self.sleep_setting_top_img_ej = setting_rest_top_ej_img
        self.sleep_setting_bottom_label = setting_rest_bottom_label
        self.setting_screen_property = [
            "常亮",
            "15s",
            "30s",
            "45s",
            "60s",
            "75s",
            "90s",
            "105s",
            "120s",
        ]
        self.sleep_setting_rest_top_net = setting_rest_top_net
        self.sleep_setting_top_img_gps = setting_rest_top_gps
        self.setting_btn_list = list()
        self.setting_update_flag = True
        self.__lcd_sleep_mode_dict = {
            0: 1,
            1: 15,
            2: 30,
            3: 45,
            4: 60,
            5: 75,
            6: 90,
            7: 105,
            8: 120
        }

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_rest_screen_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.sleep_setting_top_img_gps.set_src('gps.png')
        else:
            self.sleep_setting_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.sleep_setting_rest_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        mode = EventMesh.publish("persistent_config_get", "lcd_sleep_time_mode")
        if self.cur >= 0:
            self.__clear_setting_state()
        for k, v in self.__lcd_sleep_mode_dict.items():
            if v == mode:
                self.cur = k
                self.check_state_cur = k
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.__add_img_check_state(self.cur)
        self.load_end()
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        mode = self.__lcd_sleep_mode_dict.get(self.cur)
        old_mode = EventMesh.publish("get_lcd_sleep_mode")
        EventMesh.publish("set_lcd_sleep_mode", mode)
        if mode == 1:
            EventMesh.publish("lcd_sleep_timer_stop")
        if old_mode == 1 and mode != 1:
            EventMesh.publish("lcd_sleep_timer_start")
        self.__add_img_check_state(self.cur)

    def back(self):
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.sleep_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if self.check_state_cur == self.cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[self.cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = self.cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        if self.setting_update_flag:
            # 把之前的list删掉
            self.sleep_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.sleep_setting_list_1 = lv.list(self.comp)
            self.sleep_setting_list_1.set_pos(0, 40)
            self.sleep_setting_list_1.set_size(128, 69)
            self.sleep_setting_list_1.set_style_pad_left(2, 0)
            self.sleep_setting_list_1.set_style_pad_top(4, 0)
            self.sleep_setting_list_1.set_style_pad_row(3, 0)
            self.sleep_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.sleep_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.sleep_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)

            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.sleep_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.sleep_setting_list_1.get_child(cur)
                self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                      lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_rest_screen_group_cur_cb(self, topic, group):
        self.sleep_setting_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.sleep_setting_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.sleep_setting_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.sleep_setting_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.sleep_setting_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.sleep_setting_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.sleep_setting_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.sleep_setting_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.sleep_setting_top_img_group_id.set_src('B:/static/1.png')


class SettingCallTimeScreen(Screen):
    NAME = "setting_call_time"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 4
        self.comp = setting_call_time
        self.currentButton = None
        self.check_state_cur = None
        self.call_time_setting_list_1 = setting_call_time_screen_list
        self.call_time_top_img_battery = setting_call_time_top_battery
        self.call_time_top_img_gps = setting_call_time_top_gps
        self.call_time_top_img_group_id = setting_call_time_top_sim_id
        self.call_time_top_img_signal = setting_call_time_top_signal
        self.call_time_top_img_ej = setting_call_time_top_ej_img
        self.call_time_bottom_label = setting_call_time_bottom_label
        self.setting_screen_property = [
            "30s",
            "60s",
            "90s",
            "120s",
        ]
        self.call_time_top_net = setting_call_time_top_net
        self.setting_btn_list = list()
        self.setting_update_flag = True
        self.__single_call_quit_time_dict = {
            0: 30,
            1: 60,
            2: 90,
            3: 120
        }

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_call_time_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.call_time_top_img_gps.set_src('gps.png')
        else:
            self.call_time_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.call_time_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        mode = EventMesh.publish("persistent_config_get", "quit_call_time")
        if self.cur >= 0:
            self.__clear_setting_state()
        for k, v in self.__single_call_quit_time_dict.items():
            if v == mode:
                self.cur = k
                self.check_state_cur = k
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.__add_img_check_state(self.cur)
        self.load_end()
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        EventMesh.publish("set_single_call_quit_time", self.__single_call_quit_time_dict.get(self.cur))
        self.__add_img_check_state(self.cur)

    def back(self):
        # self.__delete_top_or_bottom()
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.call_time_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if self.check_state_cur == self.cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[self.cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = self.cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        # 把之前的list删掉
        if self.setting_update_flag:
            self.call_time_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.call_time_setting_list_1 = lv.list(self.comp)
            self.call_time_setting_list_1.set_pos(0, 40)
            self.call_time_setting_list_1.set_size(128, 69)
            self.call_time_setting_list_1.set_style_pad_left(2, 0)
            self.call_time_setting_list_1.set_style_pad_top(4, 0)
            self.call_time_setting_list_1.set_style_pad_row(3, 0)
            self.call_time_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.call_time_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.call_time_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.call_time_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.call_time_setting_list_1.get_child(cur)
                self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                      lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_call_time_group_cur_cb(self, topic, group):
        self.call_time_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.call_time_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.call_time_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.call_time_top_setting_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.call_time_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.call_time_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.call_time_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.call_time_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.call_time_top_img_group_id.set_src('B:/static/1.png')


class SettingBatteryScreen(Screen):
    NAME = "setting_battery"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 4
        self.comp = setting_battery
        self.currentButton = None
        self.check_state_cur = None
        self.battery_setting_list_1 = setting_battery_screen_list
        self.battery_setting_top_img_battery = setting_battery_top_battery
        self.battery_setting_top_img_gps = setting_battery_top_gps
        self.battery_setting_top_img_group_id = setting_battery_top_sim_id
        self.battery_setting_top_img_signal = setting_battery_top_signal
        self.battery_setting_top_img_ej = setting_battery_top_ej_img
        self.battery_setting_bottom_label = setting_battery_bottom_label
        self.battery_setting_top_net = setting_battery_top_net
        self.setting_screen_property = [
            "高性能",
            "标准",
            "省电",
            "超级省电",
        ]
        self.setting_btn_list = list()
        self.setting_update_flag = True
        self.__low_power_mode_dict = {
            0: 15,  # 高性能
            1: 30,  # 标准
            2: 45,  # 省电
            3: 50,  # 超级省电
        }

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_battery_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.battery_setting_top_img_gps.set_src('gps.png')
        else:
            self.battery_setting_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.battery_setting_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        mode = EventMesh.publish("persistent_config_get", "low_power_mode")
        if self.cur >= 0:
            self.__clear_setting_state()
        for k, v in self.__low_power_mode_dict.items():
            if v == mode:
                self.cur = k
                self.check_state_cur = k
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.__add_img_check_state(self.cur)
        self.load_end()
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        EventMesh.publish("set_poc_low_power_mode", self.__low_power_mode_dict.get(self.cur))
        self.__add_img_check_state(self.cur)

    def back(self):
        # self.__delete_top_or_bottom()
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.battery_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if self.check_state_cur == self.cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[self.cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = self.cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        if self.setting_update_flag:
            # 把之前的list删掉
            self.battery_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.battery_setting_list_1 = lv.list(self.comp)
            self.battery_setting_list_1.set_pos(0, 40)
            self.battery_setting_list_1.set_size(128, 69)
            self.battery_setting_list_1.set_style_pad_left(2, 0)
            self.battery_setting_list_1.set_style_pad_top(4, 0)
            self.battery_setting_list_1.set_style_pad_row(3, 0)
            self.battery_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.battery_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.battery_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.battery_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.battery_setting_list_1.get_child(cur)
                self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                      lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_battery_group_cur_cb(self, topic, group):
        self.battery_setting_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.battery_setting_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.battery_setting_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.battery_setting_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.battery_setting_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.battery_setting_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.battery_setting_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.battery_setting_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.battery_setting_top_img_group_id.set_src('B:/static/1.png')


class SettingSimScreen(Screen):
    NAME = "setting_sim"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 3
        self.comp = setting_sim
        self.currentButton = None
        self.check_state_cur = None
        self.sim_mode = 1
        self.sim_setting_list_1 = setting_sim_screen_list
        self.sim_setting_top_img_battery = setting_sim_top_battery
        self.sim_setting_top_img_gps = setting_sim_top_gps
        self.sim_setting_top_img_group_id = setting_sim_top_sim_id
        self.sim_setting_top_img_signal = setting_sim_top_signal
        self.sim_setting_top_img_ej = setting_sim_top_ej_img
        self.sim_setting_bottom_label = setting_sim_bottom_label
        self.sim_setting_top_net = setting_sim_top_net
        self.setting_screen_property = [
            "卡1",
            "卡2",
            "自动",
        ]
        self.setting_btn_list = list()
        self.setting_update_flag = True

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_sim_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.sim_setting_top_img_gps.set_src('gps.png')
        else:
            self.sim_setting_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.sim_setting_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        self.sim_mode = EventMesh.publish("get_sim_mode")
        sim_id = EventMesh.publish("sim_slot_get")
        if self.cur >= 0:
            self.__clear_setting_state()
        self.cur = sim_id
        self.check_state_cur = sim_id
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.setting_btn_list[self.cur][0].set_src('B:/static/check_on.png')
        self.setting_btn_list[1 - self.cur][0].set_src('B:/static/check_off.png')
        self.load_end()
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        if self.cur == 2:
            self.sim_mode = EventMesh.publish("set_sim_mode", 1 - self.sim_mode)
            self.__add_img_check_state(self.cur)
        else:
            state = EventMesh.publish("sim_slot_switch", self.cur)
            if state == -1:
                param = {"screen": self.get_comp(), "msg": "切卡失败", "font": style_siyuan_14_black}
                EventMesh.publish("msg_box_popup_show", param)
            elif state == 0:
                self.__add_img_check_state(self.cur)
                param = {"screen": self.get_comp(), "msg": "切卡成功", "font": style_siyuan_14_black}
                EventMesh.publish("msg_box_popup_show", param)

    def back(self):
        back_screen = self.meta.get("back")
        if back_screen:
            EventMesh.publish("load_screen", back_screen)
            return
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.sim_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if cur == 2:
            if self.sim_mode:
                self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
            else:
                self.setting_btn_list[cur][0].set_src('B:/static/check_off.png')
            return
        if self.check_state_cur == cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        if self.setting_update_flag:
            # 把之前的list删掉
            self.sim_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.sim_setting_list_1 = lv.list(self.comp)
            self.sim_setting_list_1.set_pos(0, 40)
            self.sim_setting_list_1.set_size(128, 69)
            self.sim_setting_list_1.set_style_pad_left(2, 0)
            self.sim_setting_list_1.set_style_pad_top(4, 0)
            self.sim_setting_list_1.set_style_pad_row(3, 0)
            self.sim_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.sim_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.sim_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.sim_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.sim_setting_list_1.get_child(cur)
                self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                      lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[cur][0].set_src("B:/static/check_on.png")
                if self.sim_mode:
                    self.setting_btn_list[2][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_sim_group_cur_cb(self, topic, group):
        self.sim_setting_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.sim_setting_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.sim_setting_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.sim_setting_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.sim_setting_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.sim_setting_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.sim_setting_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.sim_setting_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.sim_setting_top_img_group_id.set_src('B:/static/1.png')


class SettingPlatformScreen(Screen):
    NAME = "setting_platform"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 2
        self.comp = setting_platform
        self.currentButton = None
        self.check_state_cur = None
        self.platform_setting_list_1 = setting_platform_screen_list
        self.platform_top_img_battery = setting_platform_top_battery
        self.platform_top_img_gps = setting_platform_top_gps
        self.platform_top_img_group_id = setting_platform_top_sim_id
        self.platform_top_img_signal = setting_platform_top_signal
        self.platform_top_img_ej = setting_platform_top_ej_img
        self.platform_bottom_label = setting_platform_bottom_label
        self.setting_platform_top_net = setting_platform_top_net
        self.now_platform = None
        self.setting_screen_property = [
            "芯平台",
            "博纳德",
        ]
        self.setting_btn_list = list()
        self.setting_update_flag = True

    def post_processor_before_initialization(self):
        self.now_platform = EventMesh.publish("persistent_config_get", "platform")
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_platform_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.platform_top_img_gps.set_src('gps.png')
        else:
            self.platform_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.setting_platform_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        mode = self.now_platform
        if self.cur >= 0:
            self.__clear_setting_state()
        self.cur = mode
        self.check_state_cur = mode
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.__add_img_check_state(self.cur)
        self.load_end()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        self.__add_img_check_state(self.cur)
        EventMesh.publish("set_poc_platform", self.cur)

    def back(self):
        back_screen = self.meta.get("back")
        if back_screen:
            EventMesh.publish("load_screen", back_screen)
            return
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        print("SettingPlatformScreen down")
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        print("SettingPlatformScreen up")
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.platform_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if cur == 3:
            pass
        if self.check_state_cur == cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        if self.setting_update_flag:
            # 把之前的list删掉
            self.platform_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.platform_setting_list_1 = lv.list(self.comp)
            self.platform_setting_list_1.set_pos(0, 40)
            self.platform_setting_list_1.set_size(128, 69)
            self.platform_setting_list_1.set_style_pad_left(2, 0)
            self.platform_setting_list_1.set_style_pad_top(4, 0)
            self.platform_setting_list_1.set_style_pad_row(3, 0)
            self.platform_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.platform_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.platform_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.platform_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.platform_setting_list_1.get_child(cur)
                self.setting_btn_list[self.now_platform][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                               lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[self.now_platform][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                                    lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[self.now_platform][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_platform_group_cur_cb(self, topic, group):
        self.platform_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.platform_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.platform_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.platform_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.platform_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.platform_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.platform_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.platform_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.platform_top_img_group_id.set_src('B:/static/1.png')


class SettingKeypadToneScreen(Screen):
    NAME = "setting_keypad_tone"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 2
        self.comp = setting_keypad_tone
        self.currentButton = None
        self.check_state_cur = None
        self.keypad_tone_setting_list_1 = setting_keypad_tone_screen_list
        self.keypad_tone_top_img_battery = setting_keypad_tone_top_battery
        self.keypad_tone_top_img_gps = setting_keypad_tone_top_gps
        self.keypad_tone_top_img_group_id = setting_keypad_tone_top_sim_id
        self.keypad_tone_top_img_signal = setting_keypad_tone_top_signal
        self.keypad_tone_top_img_ej = setting_keypad_tone_top_ej_img
        self.keypad_tone_bottom_label = setting_keypad_tone_bottom_label
        self.setting_keypad_tone_top_net = setting_keypad_tone_top_net
        self.now_keypad_tone = None
        self.setting_screen_property = [
            "开启",
            "关闭",
        ]
        self.setting_btn_list = list()
        self.setting_update_flag = True

    def post_processor_before_initialization(self):
        self.now_keypad_tone = EventMesh.publish("persistent_config_get", "keypad_tone")
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_keypad_tone_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.keypad_tone_top_img_gps.set_src('gps.png')
        else:
            self.keypad_tone_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.setting_keypad_tone_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        mode = self.now_keypad_tone
        if self.cur >= 0:
            self.__clear_setting_state()
        self.cur = mode
        self.check_state_cur = mode
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.__add_img_check_state(self.cur)
        self.load_end()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        self.__add_img_check_state(self.cur)
        EventMesh.publish("set_poc_keypad_tone", self.cur)

    def back(self):
        back_screen = self.meta.get("back")
        if back_screen:
            EventMesh.publish("load_screen", back_screen)
            return
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        print("SettingPlatformScreen down")
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        print("SettingPlatformScreen up")
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.keypad_tone_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if cur == 3:
            pass
        if self.check_state_cur == cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        if self.setting_update_flag:
            # 把之前的list删掉
            self.keypad_tone_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.keypad_tone_setting_list_1 = lv.list(self.comp)
            self.keypad_tone_setting_list_1.set_pos(0, 40)
            self.keypad_tone_setting_list_1.set_size(128, 69)
            self.keypad_tone_setting_list_1.set_style_pad_left(2, 0)
            self.keypad_tone_setting_list_1.set_style_pad_top(4, 0)
            self.keypad_tone_setting_list_1.set_style_pad_row(3, 0)
            self.keypad_tone_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.keypad_tone_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.keypad_tone_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.keypad_tone_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.keypad_tone_setting_list_1.get_child(cur)
                self.setting_btn_list[self.now_keypad_tone][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[self.now_keypad_tone][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                                       lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[self.now_keypad_tone][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_keypad_tone_group_cur_cb(self, topic, group):
        self.keypad_tone_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.keypad_tone_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.keypad_tone_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.keypad_tone_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.keypad_tone_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.keypad_tone_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.keypad_tone_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.keypad_tone_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.keypad_tone_top_img_group_id.set_src('B:/static/1.png')


class SettingPttHintToneScreen(Screen):
    NAME = "setting_ptt_hint_tone"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 2
        self.comp = setting_ptt_hint_tone
        self.currentButton = None
        self.check_state_cur = None
        self.ptt_hint_tone_setting_list_1 = setting_ptt_hint_tone_screen_list
        self.ptt_hint_tone_top_img_battery = setting_ptt_hint_tone_top_battery
        self.ptt_hint_tone_top_img_gps = setting_ptt_hint_tone_top_gps
        self.ptt_hint_tone_top_img_group_id = setting_ptt_hint_tone_top_sim_id
        self.ptt_hint_tone_top_img_signal = setting_ptt_hint_tone_top_signal
        self.ptt_hint_tone_top_img_ej = setting_ptt_hint_tone_top_ej_img
        self.ptt_hint_tone_bottom_label = setting_ptt_hint_tone_bottom_label
        self.setting_ptt_hint_tone_top_net = setting_ptt_hint_tone_top_net
        self.now_ptt_hint_tone = None
        self.setting_screen_property = [
            "开启",
            "关闭",
        ]
        self.setting_btn_list = list()
        self.setting_update_flag = True

    def post_processor_before_initialization(self):
        self.now_ptt_hint_tone = EventMesh.publish("persistent_config_get", "ptt_hint_tone")
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.setting_ptt_hint_tone_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.ptt_hint_tone_top_img_gps.set_src('gps.png')
        else:
            self.ptt_hint_tone_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.setting_ptt_hint_tone_top_net.set_text(msg)

    def initialization(self):
        self.load_start()
        self.__load_group_cur()
        mode = self.now_ptt_hint_tone
        if self.cur >= 0:
            self.__clear_setting_state()
        self.cur = mode
        self.check_state_cur = mode
        self.__setting_screen_list_create(self.cur)
        self.__add_setting_state(self.cur)
        self.__add_img_check_state(self.cur)
        self.load_end()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        self.__add_img_check_state(self.cur)
        EventMesh.publish("set_poc_ptt_hint_tone", self.cur)

    def back(self):
        back_screen = self.meta.get("back")
        if back_screen:
            EventMesh.publish("load_screen", back_screen)
            return
        EventMesh.publish("load_screen", {"screen": "setting"})

    def down(self):
        print("SettingPlatformScreen down")
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        print("SettingPlatformScreen up")
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.__add_setting_state()

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if len(self.setting_btn_list):
            self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0x00, 0x00, 0x00),
                                                             lv.PART.MAIN | lv.STATE.DEFAULT)
            self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0x00, 0x00, 0x00),
                                                                  lv.PART.MAIN | lv.STATE.DEFAULT)

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.ptt_hint_tone_setting_list_1.get_child(cur)
        self.setting_btn_list[cur][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                         lv.PART.MAIN | lv.STATE.DEFAULT)
        self.setting_btn_list[cur][1].set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00),
                                                              lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __add_img_check_state(self, cur=None):
        if cur is None:
            cur = self.cur
        if cur == 3:
            pass
        if self.check_state_cur == cur:
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
        else:
            self.setting_btn_list[self.check_state_cur][0].set_src('B:/static/check_off.png')
            self.setting_btn_list[cur][0].set_src('B:/static/check_on.png')
            self.check_state_cur = cur

    def __setting_screen_list_create(self, cur):
        """息屏界面列表重新创建"""
        if self.setting_update_flag:
            # 把之前的list删掉
            self.ptt_hint_tone_setting_list_1.delete()
            if self.setting_btn_list:
                self.setting_btn_list = []
            # 再创建list
            self.ptt_hint_tone_setting_list_1 = lv.list(self.comp)
            self.ptt_hint_tone_setting_list_1.set_pos(0, 40)
            self.ptt_hint_tone_setting_list_1.set_size(128, 69)
            self.ptt_hint_tone_setting_list_1.set_style_pad_left(2, 0)
            self.ptt_hint_tone_setting_list_1.set_style_pad_top(4, 0)
            self.ptt_hint_tone_setting_list_1.set_style_pad_row(3, 0)
            self.ptt_hint_tone_setting_list_1.add_style(style_cont_black, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.ptt_hint_tone_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.ptt_hint_tone_setting_list_1.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                for num in range(0, self.count):
                    setting_btn = lv.btn(self.ptt_hint_tone_setting_list_1)
                    setting_btn.set_pos(20, 0)
                    setting_btn.set_size(128, 18)
                    setting_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    setting_btn_img = lv.img(setting_btn)
                    setting_btn_img.set_pos(2, 0)
                    setting_btn_img.set_size(17, 17)
                    img_path_name = ("B:/static/check_off.png")
                    setting_btn_img.set_src(img_path_name)
                    setting_label = lv.label(setting_btn)
                    setting_label.set_pos(22, 2)
                    setting_label.set_size(103, 18)
                    setting_label.set_text(self.setting_screen_property[num])
                    setting_label.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
                    self.setting_btn_list.append((setting_btn_img, setting_label, setting_btn))
                self.setting_update_flag = False
                self.currentButton = self.ptt_hint_tone_setting_list_1.get_child(cur)
                self.setting_btn_list[self.now_ptt_hint_tone][1].set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00),
                                                                                    lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[self.now_ptt_hint_tone][1].set_style_bg_grad_color(
                    lv.color_make(0xe6, 0x91, 0x00),
                    lv.PART.MAIN | lv.STATE.DEFAULT)
                self.setting_btn_list[self.now_ptt_hint_tone][0].set_src("B:/static/check_on.png")
                self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def setting_ptt_hint_tone_group_cur_cb(self, topic, group):
        self.ptt_hint_tone_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.ptt_hint_tone_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.ptt_hint_tone_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.ptt_hint_tone_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.ptt_hint_tone_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.ptt_hint_tone_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.ptt_hint_tone_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.ptt_hint_tone_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.ptt_hint_tone_top_img_group_id.set_src('B:/static/1.png')


class LbsInfoScreen(Screen):
    NAME = "location"

    def __init__(self):
        super().__init__()
        self.comp = lbs
        self.count = 3
        self.cur = 0
        self.lbs_img = lbs_img
        self.lbs_label = lbs_label
        self.lbs_top_img_battery = None
        self.lbs_top_img_gps = None
        self.lbs_top_img_group_id = None
        self.lbs_top_img_signal = None
        self.lbs_info_list = list()

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("lbs_result_event", self.lbs_result_event)

    def initialization(self):
        self.lbs_label.set_text("正在查询中...")
        EventMesh.publish("request_lbs_info")

    def get_comp(self):
        return self.comp

    def lbs_result_event(self, event=None, data=None):
        self.lbs_info_list = data
        self.lbs_label.set_text("")
        self.lbs_img.set_src(data[0])

    def ok(self):
        if self.lbs_info_list and self.lbs_info_list[3] != "":
            tts_msg = self.lbs_info_list[3].strip(" ")
            EventMesh.publish("media-tts-play", (tts_msg, 1))

    def back(self):
        self.lbs_info_list = []
        self.lbs_img.set_src("B:/static/index1.png")
        EventMesh.publish("load_screen", {"screen": "menu"})

    def up(self):
        if not self.lbs_info_list:
            return
        cur = self.cur + 1
        if cur > self.count - 1:
            pass
            # self.cur = 0
        else:
            self.cur = cur
        self.lbs_img.set_src(self.lbs_info_list[self.cur])

    def down(self):
        if not self.lbs_info_list:
            return
        cur = self.cur - 1
        if cur < 0:
            pass
        else:
            self.cur = cur
        self.lbs_img.set_src(self.lbs_info_list[self.cur])


class WeatherInfoScreen(Screen):
    NAME = "weather"

    def __init__(self):
        super().__init__()
        self.comp = weather
        self.weather_label = weather_label
        self.weather_label1 = weather_label1
        self.weather_label2 = weather_label2
        self.weather_img = weather_img
        self.weather_img1 = weather_img1
        self.weather_img2 = weather_img2
        self.weather_info_list = list()
        self.weather_msg_list = list()
        self.weather_top_img_battery = weather_top_battery
        self.weather_top_img_gps = weather_top_gps
        self.weather_top_img_group_id = weather_top_sim_id
        self.weather_top_img_signal = weather_top_signal
        self.weather_top_img_ej = weather_top_ej_img
        self.weather_bottom_label = weather_bottom_label
        self.weather_top_net = weather_top_net

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("weather_result_event", self.weather_result_event)

    def post_processor_before_initialization(self):
        if not self.weather_info_list:
            self.weather_label1.set_text("正在查询中")
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("group_cur", self.weather_group_cur_cb)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.weather_top_img_gps.set_src('gps.png')
        else:
            self.weather_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.weather_top_net.set_text(msg)

    def initialization(self):
        self.__load_group_cur()
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        EventMesh.publish("request_weather_info")
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def weather_result_event(self, event=None, data=None):
        if data:
            self.weather_info_list = data[3]
            self.weather_img.set_src(data[0][0][1])
            self.weather_label.set_text("今天 " + data[0][1])
            self.weather_img1.set_src(data[1][0][1])
            self.weather_label1.set_text("明天 " + data[1][1])
            self.weather_img2.set_src(data[2][0][1])
            self.weather_label2.set_text("后天 " + data[2][1])

    def ok(self):
        if self.weather_info_list and self.weather_info_list[0] != "":
            tts_msg = self.weather_info_list[0]
            EventMesh.publish("media-tts-play", (tts_msg, 1))

    def back(self):
        self.weather_img.set_src("B:/static/duoyun1.png")
        self.weather_img1.set_src("B:/static/duoyun1.png")
        self.weather_img2.set_src("B:/static/duoyun1.png")
        self.weather_label.set_text("")
        self.weather_label1.set_text("")
        self.weather_label2.set_text("")
        self.weather_info_list = []
        EventMesh.publish("load_screen", {"screen": "menu"})

    def down(self):
        pass

    def up(self):
        pass

    def weather_group_cur_cb(self, topic, group):
        self.weather_bottom_label.set_text(group)

    def __load_group_cur(self):
        ret = EventMesh.publish("main_get_group_cur")
        if ret:
            self.weather_bottom_label.set_text(ret)

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.weather_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.weather_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.weather_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.weather_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.weather_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.weather_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.weather_top_img_group_id.set_src('B:/static/1.png')


class AboutScreen(Screen):
    NAME = "about"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 7
        self.comp = about
        self.currentButton = None
        self.about_button = None
        self.about_top_img_battery = about_top_battery
        self.about_top_img_gps = about_top_gps
        self.about_top_img_group_id = about_top_sim_id
        self.about_top_img_signal = about_top_signal
        self.about_top_img_ej = about_top_ej_img
        self.about_label_group_title = about_label_group_title
        self.about_label_group_info = about_label_group_info
        self.about_top_net = about_top_net
        self.btn_ok_press_list = []
        self.about_show_txt_dict = {
            0: self.__load_user,
            1: self.__load_system_version,
            2: self.__load_poc_version,
            3: self.__load_fw_version,
            4: self.__load_iccid,
            5: self.__load_imei_qr_code,
            6: self.__load_standby_time
        }

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.about_top_img_gps.set_src('gps.png')
        else:
            self.about_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.about_top_net.set_text(msg)

    def initialization(self):
        self.cur = 0
        self.load_start()
        self.__load_user()
        self.load_end()
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        # 获取信号强度
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        self.__load_sim_id()

    def get_comp(self):
        return self.comp

    def ok(self):
        if self.cur == 2:
            if len(self.btn_ok_press_list) < 10:
                self.btn_ok_press_list.append(utime.mktime(utime.localtime()))
            else:
                if self.btn_ok_press_list[-1] - self.btn_ok_press_list[0] < 10:
                    self.btn_ok_press_list = []
                    EventMesh.publish("set_net_show")
                else:
                    self.btn_ok_press_list = self.btn_ok_press_list[1:9]
                    self.btn_ok_press_list.append(utime.mktime(utime.localtime()))

    def back(self):
        EventMesh.publish("qr_code_hide")
        back_screen = self.meta.get("back")
        if back_screen:
            EventMesh.publish("load_screen", back_screen)
            return
        EventMesh.publish("load_screen", {"screen": "menu"})

    def down(self):
        # 总共四元素  直接移到最末尾 4号下标位置
        cur = self.cur + 1
        if cur != self.count - 2:
            EventMesh.publish("qr_code_hide")
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.about_show_txt_dict.get(self.cur)()

    def up(self):
        # 总共四元素  直接移到最末尾 0号下标位置
        cur = self.cur - 1
        if cur != self.count - 2:
            EventMesh.publish("qr_code_hide")
        if cur < 0:
            self.cur = self.count - 1
        else:
            self.cur = cur
        self.about_show_txt_dict.get(self.cur)()

    def __load_user(self):
        dev_usr = EventMesh.publish("about_get_user")
        self.about_label_group_title.set_text("使用者:")
        self.about_label_group_info.set_text(dev_usr)
        return dev_usr

    def __load_system_version(self):
        # 系统版本
        self.about_label_group_title.set_text("系统版本:")
        self.about_label_group_info.set_text("BQ79-XIN-v1.0.1-220825")

    def __load_imei_qr_code(self):
        EventMesh.publish("qr_code_show")
        self.about_label_group_title.set_text("IMEI:")
        self.about_label_group_info.set_text(modem.getDevImei())

    def __load_fw_version(self):
        dev_fw_version = EventMesh.publish("get_poc_fw_version")
        self.about_label_group_title.set_text("固件版本:")
        self.about_label_group_info.set_text(dev_fw_version)
        return dev_fw_version

    def __load_poc_version(self):
        self.btn_ok_press_list = []
        dev_poc_version = EventMesh.publish("get_poc_version")
        self.about_label_group_title.set_text("POC版本:")
        self.about_label_group_info.set_text(dev_poc_version)
        return dev_poc_version

    def __load_iccid(self):
        iccid = sim.getIccid()
        self.about_label_group_title.set_text("ICCID:")
        if iccid == -1:
            self.about_label_group_info.set_text("")
        else:
            self.about_label_group_info.set_text(iccid)
        return iccid

    def __load_standby_time(self):
        standby_time_info = EventMesh.publish("get_standby_time")
        self.about_label_group_title.set_text("待机时间:")
        self.about_label_group_info.set_text(standby_time_info)
        return standby_time_info

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.about_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.about_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.about_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.about_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.about_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.about_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.about_top_img_group_id.set_src('B:/static/1.png')


class StdWriteNumber(Screen):
    # 伯纳德平台写号
    NAME = "std_write"

    def __init__(self):
        super().__init__()
        self.comp = std_write
        self.currentButton = None
        self.std_button = None
        self.std_write_label = std_write_label1
        self.std_top_img_battery = std_write_top_battery
        self.std_top_img_gps = std_write_top_gps
        self.std_top_img_group_id = std_write_top_sim_id
        self.std_top_img_signal = std_write_top_signal
        self.std_top_img_ej = std_write_top_ej_img
        self.std_top_net = std_write_top_net
        self.iccid = None
        self.uart = None

    def post_processor_before_initialization(self):
        EventMesh.subscribe("update_ej_img", self.update_ej_img)
        EventMesh.subscribe("signal", self.__signal_cb)
        EventMesh.subscribe("battery", self.__battery_cb)
        EventMesh.subscribe("net_show", self.__net_cb)
        EventMesh.subscribe("gps_img_state", self.__gps_cb)

    def __gps_cb(self, event, msg):
        if not msg:
            self.std_top_img_gps.set_src('gps.png')
        else:
            self.std_top_img_gps.set_src('B:/static/gps.png')

    def __net_cb(self, event, msg):
        self.std_top_net.set_text(msg)

    def initialization(self):
        # 获取信号强度
        self.uart = UART(UART.UART3, 115200, 8, 0, 1, 0)
        signal = self.publish_sig()
        self.__signal_cb(None, signal)
        EventMesh.publish("publish_net_show")
        EventMesh.publish("get_gps_img_state")
        # 获取电池电量
        battery = self.publish_battery()
        self.__battery_cb(None, battery)
        self.__load_sim_id()
        if not EventMesh.publish("get_mic_det_state"):
            self.update_ej_img(None, 1)
        else:
            self.update_ej_img(None, 0)
        _thread.start_new_thread(self.uart_read, ())

    def uart_read(self):
        while True:
            utime.sleep(1)  # 加个延时避免EC200U/EC600U运行重启
            # 返回是否有可读取的数据长度
            msgLen = self.uart.any()
            # 当有数据时进行读取
            if msgLen:
                msg = self.uart.read(msgLen)
                # 初始数据是字节类型（bytes）,将字节类型数据进行编码
                self.iccid = msg.decode()
                break
                # str
            else:
                continue
        # 及时关闭避免重复打开报错
        result = self.iccid.split("=")[1].split(";")[0].strip()
        self.std_write_label.set_text("ICCID:{}".format(result))
        EventMesh.publish("std_write_iccid", result)
        self.uart.close()

    def get_comp(self):
        return self.comp

    def ok(self):
        pass

    def back(self):
        Power.powerRestart()

    def down(self):
        pass

    def up(self):
        pass

    def __signal_cb(self, topic, sig):
        if 0 < sig <= 31:
            self.std_top_img_signal.set_src('B:/static/signal_' + str(int(sig * 5 / 31)) + '.png')
        else:
            self.std_top_img_signal.set_src('B:/static/signal_0.png')

    def __battery_cb(self, topic, battery):
        self.std_top_img_battery.set_src(battery)

    def update_ej_img(self, topic=None, mode=None):
        if mode:
            self.std_top_img_ej.set_src('B:/static/earphone.png')
        else:
            self.std_top_img_ej.set_src('B:/static/earphone1.png')

    def __load_sim_id(self):
        if EventMesh.publish("sim_slot_get"):
            self.std_top_img_group_id.set_src('B:/static/2.png')
        else:
            self.std_top_img_group_id.set_src('B:/static/1.png')


class WelcomeScreen(Screen):
    NAME = "welcome"

    def __init__(self):
        super().__init__()
        self.comp = welcome
        self.timer = osTimer()
        self.net_flag = 0
        self.cloud_sta = 0
        self.connect_field_count = 0
        self.connect_switch = False
        self.net_check_time = osTimer()

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("network_state", self.network_cb)
        EventMesh.subscribe("check_cloud_state", self.check_cloud_state)
        if sim.getStatus() != -1:
            self.timer.start(30 * 1000, 0, self.net_result_timer)
        else:
            self.net_flag = 1
            self.timer.start(3 * 1000, 0, self.net_result_timer)

    def get_comp(self):
        return self.comp

    def network_cb(self, topic, network):
        print("network_cb  network = {}".format(network))
        if network is not None:
            self.net_flag = network
        self.net_check_time.stop()
        self.net_check_time.start(60000, 1, self.check_led)
        EventMesh.publish("reset_led_timer", network)
        if self.net_flag == 2:
            import ntptime
            ntptime.settime()

    def check_led(self, *args):
        EventMesh.publish("reset_led_timer", self.net_flag)

    def check_net_status(self):
        if self.cloud_sta == 1:
            return
        if self.net_flag == 2 and self.cloud_sta == 1:
            return
        if self.net_flag == 3:
            reason = "网络异常"
        elif self.net_flag == 1:
            reason = "请插卡"
        elif self.net_flag == 2 and self.cloud_sta != 1:
            reason = "IMEI扫码注册"
        else:
            reason = "平台异常"
        if sim.getStatus() == -1:
            reason = "请插卡"
        return reason

    def net_result_timer(self, *args):
        reason = self.check_net_status()
        if not reason:
            return
        EventMesh.publish("load_screen", {"screen": "notify", "reason": reason})
        self.switch_connect()

    def switch_connect(self):
        if not self.connect_switch:
            self.connect_switch = True
            if EventMesh.publish("get_sim_mode"):
                slot = EventMesh.publish("sim_slot_get")
                EventMesh.publish("sim_slot_switch", 1 - slot)
                print("switch --------- ")

    def check_cloud_state(self, topic, cloud_sta):
        print("check_cloud_state = {} net_flag {}".format(cloud_sta, self.net_flag))
        self.cloud_sta = cloud_sta

        if cloud_sta == 1:
            self.connect_field_count = 0
            self.connect_switch = False
            EventMesh.publish("load_screen", {"screen": "main", "init": True})

        if self.connect_field_count < 20:
            self.connect_field_count += 1
        else:
            self.switch_connect()

        if self.cloud_sta == 2:
            reason = self.check_net_status()
            if not reason:
                return
            EventMesh.publish("screen_switch",
                              {"screen": "notify", "filters": ["setting_sim", "about", "setting_platform"],
                               "reason": reason})

    def ok(self):
        pass

    def back(self):
        pass

    def up(self):
        pass

    def down(self):
        pass


class Poc_Ui(object):
    def __init__(self, lcd):
        self.lv = lv
        self.screen = None
        self.lcd = lcd
        self.screen_list = []
        self.msg_box_list = []
        self.btn_lock_key = 0
        self.__speak_flag = 0
        self.member_check_count = 0
        self.__ok_btn_timer = osTimer()
        self.__lcd_sleep_timer = osTimer()

    def add_msg_box(self, msg_box):
        self.msg_box_list.append(msg_box)
        return self

    def add_screen(self, screen):
        self.screen_list.append(screen)
        return self

    def global_popup_window(self, evnet=None, data=None):
        show_msg = data.get("msg")
        param = {"screen": self.screen.get_comp(), "msg": show_msg, "font": style_siyuan_14_black}
        EventMesh.publish("msg_box_popup_show", param)

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("btn_ok_on", self.__btn_ok_on)
        EventMesh.subscribe("btn_ok_off", self.__btn_ok_off)
        EventMesh.subscribe("btn_ok_long", self.__btn_ok_long)
        EventMesh.subscribe("btn_back", self.__btn_back)
        EventMesh.subscribe("btn_back_long", self.__btn_back_long)
        EventMesh.subscribe("btn_up", self.__btn_up)
        EventMesh.subscribe("btn_down_on", self.__btn_down_on)
        EventMesh.subscribe("btn_down_off", self.__btn_down_off)
        EventMesh.subscribe("btn_down_long", self.__btn_down_long)
        EventMesh.subscribe("btn_sleep", self.__btn_sleep)
        EventMesh.subscribe("btn_ptt_on", self.__btn_ptt_on)
        EventMesh.subscribe("btn_ptt_off", self.__btn_ptt_off)
        EventMesh.subscribe("btn_ptt_long", self.__btn_ptt_long)
        EventMesh.subscribe("btn_up_long_press", self.__btn_up_long_press)
        EventMesh.subscribe("lcd_state_manage", self.__lcd_state_manage)
        EventMesh.subscribe("lcd_sleep_timer_stop", self.__lcd_sleep_timer_stop)
        EventMesh.subscribe("lcd_sleep_timer_start", self.__lcd_sleep_timer_start)
        EventMesh.subscribe("load_screen", self.lv_load)
        EventMesh.subscribe("screen_switch", self.screen_switch)
        EventMesh.subscribe("global_popup_window", self.global_popup_window)
        for box in self.msg_box_list:
            box.post_processor_after_instantiation()
        for scr in self.screen_list:
            scr.post_processor_after_instantiation()

    def screen_switch(self, event, msg):
        if self.screen is not None and self.screen.NAME not in msg["filters"]:
            print("screen_switch screen.NAME = {} filters = {}".format(self.screen.NAME, msg['filters']))
            EventMesh.publish("load_screen", msg)

    def __btn_up_long_press(self, event, msg):
        if not self.__lcd_state_manage():
            return
        if self.__get_btn_lock_status():
            return
        self.screen.up_long_press()

    def lv_load(self, event=None, msg=None):
        """
        1. 找到跳转界面
        2. 传递上级信息
        3. 初始化界面  initialization
        :param event:
        :param msg:
        :return:
        """
        for scr in self.screen_list:
            if scr.NAME == msg["screen"]:
                scr.set_meta(msg)
                scr.post_processor_before_initialization()
                init_result = scr.initialization()
                if init_result is False:
                    return
                last_screen = self.screen
                self.screen = scr
                self.screen.post_processor_after_initialization()
                self.lv.scr_load(self.screen.get_comp())
                self.screen.post_processor_after_load()
                if last_screen:
                    if last_screen.NAME != self.screen.NAME:
                        last_screen.deactivate()

    def __btn_ok_on(self, event, mode):
        """ok 按下"""
        if not self.__lcd_state_manage():
            return
        if self.__get_btn_lock_status():
            return
        if not self.__check_btn_lock_status():
            return
        if self.screen.get_load():
            self.screen.ok()

    def __btn_ok_off(self, event, mode):
        pass

    def __btn_ok_long(self, event, mode):
        if self.screen.NAME == "main":
            if not self.btn_lock_key:
                self.btn_lock_key = 1
                param = {"msg": "已锁键"}
                EventMesh.publish("top_lock_img_show")
                EventMesh.publish("switch_btn_ok_show", 1)
                self.global_popup_window(data=param)
            else:
                self.btn_lock_key = 3
                param = {"msg": "已解锁"}
                EventMesh.publish("top_lock_img_hide")
                EventMesh.publish("switch_btn_ok_show", 0)
                self.global_popup_window(data=param)
        elif self.screen.NAME == "about" and EventMesh.publish("persistent_config_get", "platform") == 1:
            EventMesh.publish("load_screen", {"screen": "std_write", "init": True})

    def __btn_back(self, event, mode):
        if self.screen.NAME == "main":
            if self.screen.back():
                if self.__get_btn_lock_status():
                    self.__lcd_state_manage()
                    return
                if self.__lcd_state():  # 未息屏状态，熄灭屏幕
                    self.__lcd_off()
                else:
                    self.__lcd_on()  # 当前为息屏状态，唤醒点亮屏幕
        else:
            if not self.__lcd_state_manage():
                return
            if self.__get_btn_lock_status():
                return
            self.screen.back()

    def __btn_back_long(self, event, mode):
        '''back 长按关机'''
        self.__lcd_state_manage()
        if self.__get_btn_lock_status():
            return
        print("即将关机------")
        Power.powerDown()

    def __btn_down_on(self, event, mode):
        if not self.__lcd_state_manage():
            return
        if self.__get_btn_lock_status():
            return
        if self.screen.get_load():
            self.screen.down()

    def __btn_down_off(self, event, mode):
        pass

    def __btn_down_long(self, event, mode):
        if self.screen.NAME == "notify":
            EventMesh.publish("load_screen", {"screen": "about", "init": True, "back": {"screen": "notify"}})

    def __btn_up(self, event, mode):
        if not self.__lcd_state_manage():
            return
        if self.__get_btn_lock_status():
            return
        if self.screen.get_load():
            self.screen.up()

    def __btn_sleep(self, event, mode):
        if not self.__lcd_state_manage():
            return
        if self.__get_btn_lock_status():
            return
        if self.screen.NAME == "main":
            return
        if self.screen.get_load():
            self.screen.ok()

    def __btn_ptt_on(self, event, mode):
        '''
        ptt 按下
        '''
        if not EventMesh.publish("about_get_rocker_arm") and EventMesh.publish("get_login_state"):
            EventMesh.publish("media-tts-play", ("您已被关闭发言", 1))
            return

    def __btn_ptt_off(self, event, mode):
        '''
        ptt 抬起
        '''
        self.__lcd_state_manage()
        if not EventMesh.publish("about_get_rocker_arm") and EventMesh.publish("get_login_state"):
            # EventMesh.publish("media-tts-play", ("您已被关闭发言", 1))
            return
        if self.screen.NAME == "member":
            if EventMesh.publish("get_member_check_list"):
                EventMesh.publish("send_select_member_list")
                return
        EventMesh.publish("ptt_led", 0)
        self.__speak_release_handle()

    def __btn_ptt_long(self, event, mode):
        '''
        ptt 长按
        '''
        if not EventMesh.publish("about_get_rocker_arm") and EventMesh.publish("get_login_state"):
            # EventMesh.publish("media-tts-play", ("您已被关闭发言", 1))
            return
        if self.screen.NAME == "member":
            if EventMesh.publish("get_member_check_list"):
                return
        if EventMesh.publish("get_speaker_state"):
            EventMesh.publish("ptt_led", 1)
        self.__speak_press_handle()
        self.__lcd_sleep_timer_stop()
        EventMesh.publish("check_call_member_status", 1)

    def __get_btn_lock_status(self, mode=None):
        if self.btn_lock_key == 2:
            param = {"msg": "请先解锁"}
            self.global_popup_window(data=param)
            return True
        else:
            return False

    def __check_btn_lock_status(self):
        if self.btn_lock_key == 1:
            self.btn_lock_key = 2
            return False
        if self.btn_lock_key == 3:
            self.btn_lock_key = 0
            return False
        return True

    def __speak_press_handle(self):
        """
        群呼按键长按按下回调函数
        长按300ms以上算长按,否则算误按
        """
        print("开始群呼")
        self.__speak_flag = EventMesh.publish("screen_speak")

    def __speak_release_handle(self):
        """
        群呼按键长按松开回调函数
        结束群呼
        """
        if self.__speak_flag:
            print("群呼结束")
            EventMesh.publish("screen_speak_end")
            self.__speak_flag = 0
            EventMesh.publish("check_call_member_status", 0)

    def __lcd_state_manage(self, event=None, mode=None):
        """LCD 状态管理"""
        if self.__lcd_state():
            if EventMesh.publish("get_lcd_sleep_mode") == 1:
                return True
            self.__lcd_sleep_timer_restart()
            return True
        else:
            self.__lcd_on()
            return False

    def __lcd_on(self):
        self.lcd.gpio.write(1)
        EventMesh.publish("lower_power", 1)  # 0 进入休眠 1 退出休眠
        self.__lcd_sleep_timer_start()

    def __lcd_off(self):
        self.lcd.gpio.write(0)
        EventMesh.publish("lower_power", 0)  # 0 进入休眠 1 退出休眠
        self.__lcd_sleep_timer_stop()  # 0 关闭息屏定时器 1 开启息屏定时器

    def __lcd_state(self):
        return self.lcd.gpio.read()

    def __auto_lcd_switch(self, *args):
        if EventMesh.publish("get_login_state"):
            if self.__lcd_state():  # 未息屏状态，熄灭屏幕
                self.__lcd_off()

    def __lcd_sleep_timer_start(self, event=None, mode=None):
        """开启息屏定时器"""
        lcd_sleep_time = EventMesh.publish("get_lcd_sleep_mode")
        if lcd_sleep_time == 1:
            self.__lcd_sleep_timer.stop()
            return
        self.__lcd_sleep_timer.start(lcd_sleep_time * 1000, 1, self.__auto_lcd_switch)

    def __lcd_sleep_timer_stop(self, event=None, mode=None):
        """息屏"""
        self.__lcd_sleep_timer.stop()

    def __lcd_sleep_timer_restart(self, event=None, mode=None):
        """重置息屏Timer"""
        self.__lcd_sleep_timer_stop()
        self.__lcd_sleep_timer_start()

    def start(self):
        self.post_processor_after_instantiation()

    def finish(self):
        lcd_sleep_time = EventMesh.publish("get_lcd_sleep_mode")
        if lcd_sleep_time == 1:
            pass
        else:
            self.__lcd_sleep_timer_start()
