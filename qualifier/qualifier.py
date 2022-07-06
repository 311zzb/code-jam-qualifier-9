import typing
from random import randrange
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        # Get the scope from the request
        scope: typing.Mapping[str, typing.Any] = request.scope

        # Get the type of the request
        request_type: str = scope['type']

        # React to the request
        match request_type:
            case 'staff.onduty':
                staff_id: str = scope['id']
                self.staff[staff_id] = request
            case 'staff.offduty':
                staff_id: str = scope['id']
                del self.staff[staff_id]
            case 'order':
                order_speciality: str = scope['speciality']
                available_staffs: typing.List[Request] = self.find_staffs(order_speciality)
                # TODO: deal with the case when there is no staff available
                chosen_staff: Request = available_staffs[randrange(len(available_staffs))]
                await self.order_io(request, chosen_staff)

    async def order_io(self, order_request: Request, staff: Request) -> None:
        """Handle an order request.

        :param order_request: request object
            The order request object.
        :param staff: request object
            The chosen staff object.
        """
        full_order = await order_request.receive()
        # TODO: mark the staff is currently busy?
        await staff.send(full_order)

        result = await staff.receive()
        await order_request.send(result)

    def find_staffs(self, speciality: str) -> typing.List[Request]:
        """Find staff with the given speciality.

        :param speciality: speciality to look for
        :return: list of staff with the given speciality
        """
        return [s for s in self.staff.values() if speciality in s.scope['speciality']]
