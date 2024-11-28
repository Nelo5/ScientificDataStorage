import { useState, useEffect, useRef } from "react";
import {
  ChakraProvider,
  Container,
  Heading,
  Center,
  VStack,
  Text,
  HStack,
  Button,
  SimpleGrid,
  Spinner,
  Input,
  Link,
  Box,
} from "@chakra-ui/react";

export default function App() {
  const [allFiles, setAllFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isSelected, setIsSelected] = useState(false);
  const [uploadSuccessful, setUploadSuccessful] = useState(false);
  const [showSpinner, setShowSpinner] = useState(false);
  const [fileAuthor, setFileAuthor] = useState("");
  const fileInputRef = useRef(null); // Reference to hidden file input

  const onInputChange = (e) => {
    setIsSelected(true);
    setSelectedFile(e.target.files[0]);
  };

  const onFileUpload = (e) => {
    setShowSpinner(true);
    const formData = new FormData();
    formData.append("file", selectedFile, selectedFile.name);
    formData.append("author", fileAuthor);

    fetch("http://localhost:8000/files", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setUploadSuccessful(!uploadSuccessful);
        setShowSpinner(false);
        setFileAuthor("");
      })
      .catch((error) => {
        console.error("Error uploading file:", error);
        setShowSpinner(false);
      });
  };

  const triggerFileInput = () => {
    // Triggers the hidden file input click
    fileInputRef.current.click();
  };

  useEffect(() => {
    fetch("http://localhost:8000/files")
      .then((response) => response.json())
      .then((data) => {
        setAllFiles(data);
      });
  }, [uploadSuccessful]);

  return (
    <ChakraProvider>
      <Box bg="black" minHeight="100vh" color="green.300" padding={8}>
        <Center>
          <VStack spacing={7} align="center">
            <Heading as="h1" size="2xl" textTransform="uppercase" color="green.400">
              Хранилище научных данных
            </Heading>
            <Text fontSize="xl" color="green.200">
              Загрузите ваши файлы и просмотрите доступные данные
            </Text>
            <VStack
              spacing={5}
              bg="green.900"
              padding={6}
              borderRadius="lg"
              boxShadow="lg"
              width={{ base: "90%", md: "60%" }}
            >
              <Input
                type="text"
                placeholder="Имя создателя"
                value={fileAuthor}
                onChange={(e) => setFileAuthor(e.target.value)}
                size="lg"
                focusBorderColor="green.400"
                bg="black"
                color="green.300"
                _placeholder={{ color: "green.600" }}
              />
              <HStack spacing={4} width="100%">
                <Input
                  type="file"
                  ref={fileInputRef}
                  onChange={onInputChange}
                  display="none" // Hides the input field
                />
                <Button
                  size="lg"
                  colorScheme="green"
                  onClick={triggerFileInput} // Calls the function to trigger file input click
                >
                  Выберите файл
                </Button>
                <Button
                  size="lg"
                  colorScheme="green"
                  isDisabled={!isSelected}
                  onClick={onFileUpload}
                >
                  Загрузить файл
                </Button>
              </HStack>
              {selectedFile && (
                <Text color="green.300">Выбранный файл: {selectedFile.name}</Text>
              )}
              {showSpinner && <Spinner size="lg" color="green.300" />}
              <Button
                  size="lg"
                  colorScheme="green"
                  onClick={() => window.location.href = ""}
                  style={{ fontSize: '0.8rem' }} // Уменьшаем размер текста
                >
                  Перейти в JupyterNotebook для работы с файлами. Пароль для входа - password
                </Button>
            </VStack>
          </VStack>
        </Center>
        <Container maxW="container.lg" mt={10}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            {allFiles.map((file) => {
              return (
                <Box
                  key={file.id}
                  bg="green.900"
                  p={4}
                  borderRadius="md"
                  boxShadow="md"
                  transition="transform 0.2s"
                  _hover={{ transform: "scale(1.05)", boxShadow: "lg" }}
                >
                  <Link
                    href={`http://localhost:8000/files/download/${encodeURIComponent(file.file_name)}`}
                    isExternal
                    color="green.200"
                    fontWeight="bold"
                    _hover={{ color: "green.400", textDecoration: "underline" }}
                  >
                    <Text>Имя файла: {file.file_name}</Text>
                  </Link>
                  <Text color="green.300">Автор: {file.file_author}</Text>
                </Box>
              );
            })}
          </SimpleGrid>
        </Container>
      </Box>
    </ChakraProvider>
  );
}
