from langchain_core.tools import tool

@tool("book_appointment", description="Book a medical appointment for a given date, time, and patient.")
def booking_appointment(fecha: str, tiempo: str, doctor: str, patient: str) -> str:
    # Aquí iría la lógica real: validar, reservar y manejar errores
    # Mock de confirmación de cita
    return f"Appointment booked for {fecha} at {tiempo} with Dr. {doctor} for patient {patient}."


@tool("get_appointment_availability", description="Get the availability of a medical appointment for a given date, time, and doctor.")
def get_appointment_availability(fecha: str, tiempo: str, doctor: str) -> str:
    # Aquí iría la lógica real: consultar agenda y formatear 'slots' útiles
    # Mock de disponibilidad
    return f"""\
    The availability slots for Dr. {doctor} are:
    - Monday: 10:00-15:00
    - Wednesday: 10:00-15:00
    - Thursday: 10:00-15:00
    - Friday: 10:00-12:00
    """

tools = [booking_appointment, get_appointment_availability]