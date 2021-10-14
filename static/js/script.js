$(document).ready(function() {
        var mslider= {
            loop:!0, spaceBetween:30, effect:'fade', pagination: {
                el: '.mainslider-btn', clickable: !0,
            }
            , navigation: {
                nextEl: '#mslider-nbtn', prevEl: '#mslider-pbtn',
            }
            , autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            ,
        }
        var incslider= {
            slidesPerView:4, spaceBetween:10, loop: true, autoplay: {
                delay: 2000, disableOnInteraction: !1,
            }
            , breakpoints: {
            1024: {
                slidesPerView: 4,
                spaceBetween: 10,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 10,
            },
            640: {
                slidesPerView: 2,
                spaceBetween: 10,
            },
            400: {
                slidesPerView: 1,
                spaceBetween: 10,
            }
        }
        }
    var spslider= {
        slidesPerView:4, spaceBetween:10, autoplay: {
            delay: 2000, disableOnInteraction: !1,
        }
        , breakpoints: {
            1024: {
                slidesPerView: 4,
                spaceBetween: 10,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 10,
            },
            640: {
                slidesPerView: 2,
                spaceBetween: 10,
            },
            400: {
                slidesPerView: 1,
                spaceBetween: 10,
            }
        }
    }
        var pslider= {
            slidesPerView:4, spaceBetween:10, autoplay: {
                delay: 2000, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#pslider-nbtn', prevEl: '#pslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var pslider= {
            slidesPerView:5, spaceBetween:10, autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#pslider-nbtn', prevEl: '#pslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var vpslider= {
            slidesPerView:5, spaceBetween:10, autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#vpslider-nbtn', prevEl: '#vpslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var mvpslider= {
            slidesPerView:5, spaceBetween:10, autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#mvpslider-nbtn', prevEl: '#mvpslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var newpslider= {
            slidesPerView:5, spaceBetween:10, autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#newpslider-nbtn', prevEl: '#newpslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var mostpslider= {
            slidesPerView:5, spaceBetween:10, autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#mostpslider-nbtn', prevEl: '#mostpslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var brandslider= {
            slidesPerView:5, spaceBetween:10, autoplay: {
                delay: 2500, disableOnInteraction: !1,
            }
            , navigation: {
                nextEl: '#brandslider-nbtn', prevEl: '#brandslider-pbtn',
            }
            , breakpoints: {
                1024: {
                    slidesPerView: 4, spaceBetween: 10,
                }
                , 768: {
                    slidesPerView: 3, spaceBetween: 10,
                }
                , 640: {
                    slidesPerView: 2, spaceBetween: 10,
                }
                , 320: {
                    slidesPerView: 1, spaceBetween: 10,
                }
            }
        }
        var swiper=new Swiper('#mainslider', mslider);
        var swiper=new Swiper('#inc-slider', incslider);
        var swiper=new Swiper('#sp-slider', spslider);
        var swiper=new Swiper('#pslider', pslider);
        var swiper=new Swiper('#vpslider', vpslider);
        var swiper=new Swiper('#newpslider', newpslider);
        var swiper=new Swiper('#mostpslider', mostpslider);
        var swiper=new Swiper('#brandslider', brandslider);
        var swiper=new Swiper('#mvpslider', mvpslider);
        $(window).load(function() {
                $('.c-gallery__items img').click(function() {
                        var src=$(this).attr('src');
                        $('.c-gallery__img img').attr('src', src)
                    }
                );
                $('.xzoom').elevateZoom( {
                        zoomType: "inner", cursor: "crosshair"
                    }
                )
            }
        );
        $('.c-box-tabs__tab').click(function(e) {
                e.preventDefault();
                $('.c-box-tabs__tab').removeClass('is-active');
                $(this).addClass('is-active');
                var id=$(this).children('a').attr('id');
                $(".c-box--tabs > div").removeClass('is-active');
                $(".c-box--tabs > div#"+id).addClass('is-active')
            }
        );
        $('.c-mask__handler').click(function(e) {
                e.preventDefault();
                if(!$(this).hasClass('is-active')) {
                    $('.c-mask__text').attr('style', '');
                    $('.c-mask__handler').addClass('without-after');
                    $('.c-mask__handler').css('position', 'static');
                    $('.c-mask__handler').css('display', 'block');
                    $('.c-mask__handler').html('بستن');
                    $(this).addClass('is-active')
                }
                else {
                    $(this).removeClass('is-active');
                    $('.c-mask__text').attr('style', 'max-height: 250px;height: unset;');
                    $('.c-mask__handler').removeClass('without-after');
                    $('.c-mask__handler').css('position', 'absolute');
                    $('.c-mask__handler').html('ادامه مطلب')
                }
            }
        );
        var topcart=$('.top-head .cart .count');
        $('.remodal-close').click(function() {
                $('body').removeClass('main-cart-overlay');
                $('.modal-avatar__content').fadeOut(200)
            }
        );
        $('#avatar-modal').click(function() {
                $('body').addClass('main-cart-overlay');
                $('.modal-avatar__content').fadeIn(200)
            }
        );
        $('.close-modal').click(function() {
                $('.body').removeClass('main-cart-overlay');
                $('.modal-checkout').fadeOut(200)
            }
        );
        $('#addnewaddr').click(function() {
                $('.body').addClass('main-cart-overlay');
                $('.modal-checkout').fadeIn(200)
            }
        );
        $('#circle_input').change(function() {
                if($(this).is(':checked')) {
                    $('#circle').animate( {
                            right: '-7px'
                        }
                        , 300, function() {
                            $('.scroll').animate( {
                                    'background-color': 'rgb(46, 149, 9) !important', opacity: '0.8'
                                }
                            )
                        }
                    )
                }
                else {
                    $('#circle').animate( {
                            right: '20px'
                        }
                        , 300, function() {
                            $('.scroll').animate( {
                                    'background-color': 'rgb(255,255,255) !important', opacity: '0.8'
                                }
                            )
                        }
                    )
                }
            }
        );
        $(function() {
                $('#mynavmenu').slicknav( {
                        label: "منوی اصلی", prependTo: "body"
                    }
                )
            }
        );
        $('.jump-to-up').click(function() {
                $('html').animate( {
                        scrollTop: 0
                    }
                    , 500)
            }
        );
        $("#logreg").click(function() {
                $(".top-head .user-modal").fadeToggle()
            }
        );
        $('#clock').countdown('2018/11/12 16:22', function(event) {
                $(this).html(event.strftime('%H:%M:%S'))
            }
        );
        $('.persianumber').persiaNumber();

        $('#sfl-cart').click(function () {
            $('#cart-sfl').show();
            $('.c-checkout,.o-page__aside').hide();
            $('#main-cart').children('span').removeClass('c-checkout__tab--active');
            $('#main-cart').children('.c-checkout__tab-counter').css({backgroundColor: "#bbb"});
            $(this).children('span').addClass('c-checkout__tab--active');
        });
        $('#main-cart').click(function () {
            $('#cart-sfl').hide();
            $('.c-checkout,.o-page__aside').show();
            $('#main-cart .c-checkout-text').addClass('c-checkout__tab--active');
            $('#main-cart').children('.c-checkout__tab-counter').css({backgroundColor: "#ef394e"});
            $('#sfl-cart .c-checkout-text').removeClass('c-checkout__tab--active');

        });

    // suppliers
    $('.c-table-suppliers-more').click(function () {
        $( ".c-table-suppliers__body .c-table-suppliers__row" ).each(function() {
            if(! $(this).hasClass('in-list') ) $(this).addClass('in-list')
        });
        $(this).addClass('c-table-suppliers-hidden'); $('.c-table-suppliers-less').removeClass('c-table-suppliers-hidden');
    });
    $('.c-table-suppliers-less').click(function () {
        var counter = 0;
        $( ".c-table-suppliers__body .c-table-suppliers__row" ).each(function() {
            counter++;
            if(counter <= 2) return;
            if( $(this).hasClass('in-list') ) $(this).removeClass('in-list');
        });
        $(this).addClass('c-table-suppliers-hidden'); $('.c-table-suppliers-more').removeClass('c-table-suppliers-hidden');
    });

    $(window).scroll(function () {
        if($(window).scrollTop() > 110) {
            $("header").not(".shipping").addClass('sticky','nav-shadow');
            $(".top-nav").slideUp(500);
        } else {
            $("header").not(".shipping").removeClass('sticky','nav-shadow');
            $(".top-nav").slideDown(500);
        }
    });

    } // document-ready

)