(function($){
	$.fn.wish = function() {
		var _this = this;
        //get the body area height(backlog/ongoing/pending/done weight is a little less than this value).
        main_area_height = $("body").height();
		var _wish = _this.children();
		var _wish_len = _wish.length;
		var wish = {
			area:{
				left:0,
				top:0,
				right: _this.width(),
				bottom: _this.height()
			},
            skin:{
                width: 225,
                height: 206
            }
		};
		$.extend(wish);
	
		var _left = wish.area.left;
		//var _right = wish.area.right;
        var _right = 290; // the html value 200px is not appropriate here, so set to 300.
		var _top = wish.area.top;
		var _bottom = wish.area.bottom;
		
		_right = _right - _left > wish.skin.width ? _right : _left + wish.skin.width;
		_bottom = _bottom - _top > wish.skin.height ? _bottom : _top + wish.skin.height;
		_right = _right - wish.skin.width;
		_bottom = _bottom - wish.skin.height;
		var methods = {
			rans : function(v1,v2){
				var ran = parseInt(Math.random() * (v2 - v1) + v1);
				return ran;
			},
			pos : function(){
				return {left:methods.rans(_left, _right), top:methods.rans(_top, _bottom)}
			},
			css : function(){
				return methods.rans(1,5);
			}
		}

		if(_wish_len > 0)
		{
			first_element_value = _wish.get(0).value;
			//first_element_value = first_element_value % 10;
		}
		_wish.each(function(i){
			var _p = methods.pos();
			var _s = methods.css();
			var _self = $(this);
            
            //remove old algorithm for the random height of each card, but it's not very good-looking for large-scale screen( just so so for laptop).
			var orderID = _self.val();

            _left_pos = Math.random();
            
            task_key_id = _self.attr("id");
            task_key_id = task_key_id.split('_')[0];

            //new algorithm for the random height of each card.
            orderID_new = _self.height() * 0.3 + (i * (_self.height() - 10));
            while(orderID_new >= main_area_height*0.8 - _self.height())
            {
                j = (orderID_new - main_area_height*0.8) / _self.height();
                orderID_new = 60 + (j * (_self.height()));
                vertical_area_width = _this.parent().parent().width();
                max_pos = vertical_area_width * 0.5 > wish.area.right ? wish.area.right : 45;
                _left_pos = max_pos + (15 * Math.random());
            }
			_self.prepend('<a href="javascript:delete_task('+task_key_id+');" class="wish-close"></a>');
			_self.addClass('wish').addClass('s'+_s).css({'position':'absolute', 'left':_left_pos + 'px', 'top':orderID_new + 'px'});
			_self.hover(function(){
				_self.css({'z-index':'9999','border':'none'}).children('.wish-close').show().bind('click',function(){_self.effect('scale',{percent: 0},200,function(){_self.remove()})});
			},function(){
				_self.css({'z-index':'','border':'none'}).children('.wish-close').hide();
			});
		});
	};
})(jQuery);