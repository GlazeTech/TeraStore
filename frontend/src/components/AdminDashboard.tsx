import {
	Button,
	Card,
	Divider,
	Group,
	Modal,
	Select,
	Table,
	Text,
	TextInput,
} from "@mantine/core";
import { useDisclosure, useListState } from "@mantine/hooks";
import { notifications, showNotification } from "@mantine/notifications";
import {
	addDevice,
	addDeviceAttribute,
	deleteDeviceAttribute,
	getDevices,
} from "api";
import {
	deleteUser as deleteUserOnBackend,
	getUsers,
	updateUser as updateUserOnBackend,
} from "auth";
import { getEnumKeys } from "helpers";
import {
	BackendAuthLevel,
	BackendDeviceAttr,
	BackendTHzDevice,
	BackendUser,
} from "interfaces";
import { useEffect, useState } from "react";
import Header from "./Header";

export default function AdminDashboard() {
	const [users, usersHandler] = useListState<BackendUser>(undefined);

	useEffect(() => {
		getUsers().then((res) => {
			usersHandler.setState(res);
		});
	}, []);

	const updateUsers = (user: BackendUser) => {
		usersHandler.setItem(
			users.findIndex((u) => u.email === user.email),
			user,
		);
	};

	const deleteUser = (user: BackendUser) => {
		const isConfirmed = window.confirm(
			"Are you sure you want to delete this user?",
		);
		if (!isConfirmed) {
			return;
		}
		deleteUserOnBackend(user).then((res) => {
			if (res.status === 200) {
				notifications.show({
					title: "Success",
					message: "User deleted.",
					autoClose: 1000,
				});
				usersHandler.remove(users.findIndex((u) => u.email === user.email));
			}
		});
	};

	if (!users) {
		return <>Loading...</>;
	} else {
		return (
			<>
				<Header />
				<Divider m={5} />
				<div
					style={{
						display: "flex",
						justifyContent: "center",
					}}
				>
					<Group justify="space-between">
						<DevicesCard />
						<UsersCard
							users={users}
							updateUsers={updateUsers}
							deleteUser={deleteUser}
						/>
					</Group>
				</div>
			</>
		);
	}
}

function UsersCard({
	users,
	updateUsers,
	deleteUser,
}: {
	users: BackendUser[];
	updateUsers: (user: BackendUser) => void;
	deleteUser: (user: BackendUser) => void;
}) {
	return (
		<Card mt={20} shadow="xs" padding="md" withBorder pos={"relative"}>
			<Text size="xl">Unauthorized users</Text>
			<Card.Section inheritPadding>
				<UserTable
					users={users.filter(
						(user) => user.auth_level === BackendAuthLevel.UNAUTHORIZED,
					)}
					updateUsers={updateUsers}
					deleteUser={deleteUser}
				/>
			</Card.Section>
			<Text size="xl">Authorized users</Text>
			<Card.Section inheritPadding>
				<UserTable
					users={users.filter(
						(user) => user.auth_level !== BackendAuthLevel.UNAUTHORIZED,
					)}
					updateUsers={updateUsers}
					deleteUser={deleteUser}
				/>
			</Card.Section>
		</Card>
	);
}

function UserTable({
	users,
	updateUsers,
	deleteUser,
}: {
	users: BackendUser[];
	updateUsers: (user: BackendUser) => void;
	deleteUser: (user: BackendUser) => void;
}) {
	const setAuthLevel = (user: BackendUser, newAuthLevel: string | null) => {
		if (newAuthLevel === null) {
			return;
		}

		const updatedUser = { ...user };
		updatedUser.auth_level =
			BackendAuthLevel[newAuthLevel as keyof typeof BackendAuthLevel];
		updateUserOnBackend(updatedUser).then((res) => {
			if (res.status === 200) {
				notifications.show({
					title: "Success",
					message: "User updated.",
					autoClose: 1000,
				});
				updateUsers(updatedUser);
			}
		});
	};

	return (
		<Table>
			<Table.Thead>
				<Table.Tr>
					<Table.Th>Email</Table.Th>
					<Table.Th>Authorization level</Table.Th>
					<Table.Th> </Table.Th>
				</Table.Tr>
			</Table.Thead>
			<Table.Tbody>
				{users.map((user) => (
					<Table.Tr key={user.email}>
						<Table.Td>{user.email}</Table.Td>
						<Table.Td>
							<Select
								data={getEnumKeys(BackendAuthLevel)}
								defaultValue={BackendAuthLevel[user.auth_level]}
								onChange={(value) => setAuthLevel(user, value)}
							/>
						</Table.Td>
						<Table.Td>
							<Button color="red" onClick={() => deleteUser(user)}>
								Delete
							</Button>
						</Table.Td>
					</Table.Tr>
				))}
			</Table.Tbody>
		</Table>
	);
}

function DevicesCard() {
	const [modalIsOpen, modalHandler] = useDisclosure(false);
	const [newSerialNumberValue, setNewSerialNumberValue] = useState("");
	const [devices, devicesHandler] = useListState<BackendTHzDevice>(undefined);

	useEffect(() => {
		getDevices().then((res) => {
			devicesHandler.setState(res);
		});
	}, []);

	const addDeviceOnBackend = (deviceSerialNumber: string) => {
		addDevice(deviceSerialNumber)
			.then(() => {
				notifications.show({
					title: "Success",
					message: "Device added.",
					autoClose: 2000,
				});
				modalHandler.toggle();
				devicesHandler.append({
					serial_number: deviceSerialNumber,
					attributes: [],
				});
			})
			.catch((err) => {
				notifications.show({
					title: "Error",
					message: err.response.data.detail,
					autoClose: 4000,
					color: "red",
				});
			});
	};
	return (
		<Card mt={20} shadow="xs" padding="md" withBorder pos={"relative"}>
			<Modal
				opened={modalIsOpen}
				onClose={modalHandler.close}
				title={"Add device"}
			>
				<TextInput
					label="Serial number"
					placeholder="Serial number"
					onChange={(event) =>
						setNewSerialNumberValue(event.currentTarget.value)
					}
				/>
				<Button
					color="blue"
					onClick={() => addDeviceOnBackend(newSerialNumberValue)}
				>
					Add
				</Button>
			</Modal>
			<Group justify="space-between">
				<Text size="xl">Devices</Text>
				<Button color="blue" onClick={modalHandler.toggle}>
					Add device
				</Button>
			</Group>
			<Card.Section inheritPadding>
				<DeviceTable devices={devices} />
			</Card.Section>
		</Card>
	);
}

function DeviceTable({
	devices,
}: {
	devices: BackendTHzDevice[];
}) {
	return (
		<Table>
			<Table.Thead>
				<Table.Tr>
					<Table.Th>Serial number</Table.Th>
					<Table.Th> </Table.Th>
				</Table.Tr>
			</Table.Thead>
			<Table.Tbody>
				{devices.map((device) => (
					<DeviceRow device={device} key={device.serial_number} />
				))}
			</Table.Tbody>
		</Table>
	);
}

function DeviceRow({
	device,
}: {
	device: BackendTHzDevice;
}) {
	const [modalIsOpen, modalHandler] = useDisclosure(false);
	const [addAttrModalIsOpen, addAttrModalHandler] = useDisclosure(false);
	const [newAttrKey, setNewAttrKey] = useState("");
	const [newAttrValue, setNewAttrValue] = useState("");

	const addDeviceAttrOnBackend = () => {
		const newDeviceAttr: BackendDeviceAttr = {
			key: newAttrKey,
			value: parseAttrInput(newAttrValue),
			serial_number: device.serial_number,
		};
		addDeviceAttribute(newDeviceAttr)
			.then(() => {
				const refreshDuration = 2000;
				showNotification({
					title: "Success",
					message: "Attribute added.",
					autoClose: refreshDuration,
				});

				setTimeout(() => {
					window.location.reload();
				}, refreshDuration - 500);
			})
			.catch((err) => {
				showNotification({
					title: "Error",
					message: err.response.data.detail,
					autoClose: 2000,
					color: "red",
				});
			});
	};
	return (
		<Table.Tr>
			<Modal
				opened={modalIsOpen}
				onClose={modalHandler.close}
				title={device.serial_number}
			>
				<Modal
					opened={addAttrModalIsOpen}
					onClose={addAttrModalHandler.close}
					title={"Add attribute"}
				>
					<TextInput
						label="Key"
						placeholder="Key"
						onChange={(event) => setNewAttrKey(event.currentTarget.value)}
					/>
					<TextInput
						label="Value"
						placeholder="Value"
						onChange={(event) => setNewAttrValue(event.currentTarget.value)}
					/>
					<Group>
						<Button color="blue" size="xs" onClick={addDeviceAttrOnBackend}>
							Add
						</Button>
					</Group>
				</Modal>
				<Button size="xs" onClick={addAttrModalHandler.toggle}>
					Add attribute
				</Button>
				{device.attributes.map((v) => (
					<DeviceRowContent
						device={v}
						key={v.serial_number + v.key}
						modalToggler={modalHandler}
					/>
				))}
			</Modal>
			<Table.Td>{device.serial_number}</Table.Td>
			<Table.Td>
				<Button size="xs" m={5} color="blue" onClick={modalHandler.toggle}>
					Attributes
				</Button>
			</Table.Td>
		</Table.Tr>
	);
}

function DeviceRowContent({
	device,
	modalToggler,
}: {
	device: BackendDeviceAttr;
	modalToggler: {
		readonly open: () => void;
		readonly close: () => void;
		readonly toggle: () => void;
	};
}) {
	const displayValue = (attr: BackendDeviceAttr) => {
		if (attr.value instanceof Array) {
			return formatArrayToString(attr.value);
		}
		return attr.value;
	};

	const deleteAttribute = (deviceAttr: BackendDeviceAttr) => {
		const isConfirmed = window.confirm(
			"Are you sure you want to delete this attribute?",
		);
		if (!isConfirmed) {
			return;
		}
		deleteDeviceAttribute(deviceAttr).then((res) => {
			if (res.status === 200) {
				const refreshDuration = 1500;
				modalToggler.close();
				notifications.show({
					title: "Success",
					message: "Attribute deleted.",
					autoClose: refreshDuration,
				});
				setTimeout(() => {
					window.location.reload();
				}, refreshDuration - 500);
			}
		});
	};
	return (
		<Group justify="space-between">
			<Text>{device.key}</Text>
			<Group>
				<Text>{displayValue(device)}</Text>
				<Button
					size="xs"
					m={5}
					color="red"
					onClick={() => deleteAttribute(device)}
				>
					Delete
				</Button>
			</Group>
		</Group>
	);
}

function formatArrayToString(arr: number[]): string {
	const formatter = (arr: number[]) => {
		return arr
			.map((num) => {
				if (Number.isInteger(num)) {
					return num.toString();
				} else {
					const formattedNum = num.toFixed(2);
					if (formattedNum.endsWith("00")) {
						return num.toExponential(2);
					} else {
						return formattedNum;
					}
				}
			})
			.join(", ");
	};

	if (arr.length > 2) {
		return `[${formatter(arr.slice(0, 1))},..., ${arr[arr.length - 1]}]`;
	} else {
		return `[${formatter(arr)}]`;
	}
}

const parseAttrInput = (input: string): string | number | number[] => {
	const trimmedInput = input.trim();

	// Check if the input is a number
	if (!isNaN(Number(trimmedInput))) {
		return Number(trimmedInput);
	}

	// Check if the input is an array of numbers
	if (trimmedInput.startsWith("[") && trimmedInput.endsWith("]")) {
		const numbers = trimmedInput
			.slice(1, -1)
			.split(",")
			.map((item) => Number(item.trim()));

		// Check if all items in the array are valid numbers
		if (numbers.every((item) => !isNaN(item))) {
			return numbers;
		}
	}

	// If the input is not a number or an array of numbers, return it as a string
	return trimmedInput;
};
