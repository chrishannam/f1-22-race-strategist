# import functools
# import os
#
# from opentelemetry import trace
#
#
# def time_method(func):
#     """
#     Decorator to send span timing to Jaeger agent.
#     """
#
#     @functools.wraps(func)
#     def opentelemetry_timer_wrapper(*args, **kwargs):
#         # bypass timing process
#         if not os.getenv('OPENTELEMETRY_ENDPOINT'):
#             return func(*args, **kwargs)
#
#         tracer = trace.get_tracer(__name__)
#         with tracer.start_as_current_span(func.__name__):
#             return func(*args, **kwargs)
#
#     return opentelemetry_timer_wrapper
