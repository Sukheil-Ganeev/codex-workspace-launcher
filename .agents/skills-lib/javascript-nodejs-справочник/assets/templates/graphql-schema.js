/**
 * GraphQL Schema Template
 *
 * Production-ready GraphQL schema с:
 * - Type definitions
 * - Resolvers
 * - Authentication/Authorization
 * - Error handling
 *
 * @example
 * npm install apollo-server-express graphql
 */

const { gql, ApolloError } = require('apollo-server-express');

// ==================== TYPE DEFINITIONS ====================

const typeDefs = gql`
  # Scalar types
  scalar DateTime

  # Enums
  enum BookingStatus {
    PENDING
    CONFIRMED
    COMPLETED
    CANCELLED
  }

  enum UserRole {
    USER
    ADMIN
    MODERATOR
  }

  # Types
  type User {
    id: ID!
    email: String!
    name: String!
    role: UserRole!
    createdAt: DateTime!
    bookings: [Booking!]!
  }

  type Booking {
    id: ID!
    userId: ID!
    user: User!
    tourName: String!
    tourDate: DateTime!
    numberOfPeople: Int!
    totalPrice: Float!
    status: BookingStatus!
    notes: String
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  # Query (read operations)
  type Query {
    # Get single user
    me: User
    user(id: ID!): User

    # Get all users (admin only)
    users(limit: Int, skip: Int): [User!]!

    # Get bookings
    booking(id: ID!): Booking
    myBookings(status: BookingStatus): [Booking!]!
    bookings(userId: ID, limit: Int): [Booking!]!

    # Search
    searchBookings(tourName: String!): [Booking!]!
  }

  # Mutation (write operations)
  type Mutation {
    # User operations
    updateProfile(name: String, email: String): User!

    # Booking operations
    createBooking(input: CreateBookingInput!): Booking!
    updateBooking(id: ID!, input: UpdateBookingInput!): Booking!
    cancelBooking(id: ID!): Booking!
  }

  # Subscription (real-time)
  type Subscription {
    bookingCreated: Booking!
    bookingUpdated(bookingId: ID!): Booking!
  }

  # Input types
  input CreateBookingInput {
    tourName: String!
    tourDate: DateTime!
    numberOfPeople: Int!
    totalPrice: Float!
    notes: String
  }

  input UpdateBookingInput {
    tourName: String
    status: BookingStatus
    notes: String
  }

  # Error
  type Error {
    message: String!
    code: String!
  }
`;

// ==================== RESOLVERS ====================

const resolvers = {
  // ================ QUERY ================

  Query: {
    /**
     * Получить текущего пользователя
     */
    me: async (_, __, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Получить из БД
      return {
        id: user.sub,
        email: user.email,
        name: 'John Doe',
        role: user.role,
        createdAt: new Date(),
      };
    },

    /**
     * Получить пользователя по ID
     */
    user: async (_, { id }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Получить из БД
      if (id !== user.sub && user.role !== 'ADMIN') {
        throw new ApolloError('Access denied', 'FORBIDDEN');
      }

      return {
        id,
        email: 'user@example.com',
        name: 'John Doe',
        role: 'USER',
        createdAt: new Date(),
      };
    },

    /**
     * Получить всех пользователей (только для админов)
     */
    users: async (_, { limit = 10, skip = 0 }, { user }) => {
      if (!user || user.role !== 'ADMIN') {
        throw new ApolloError('Access denied', 'FORBIDDEN');
      }

      // TODO: Получить из БД с пагинацией
      return [];
    },

    /**
     * Получить бронирование по ID
     */
    booking: async (_, { id }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Получить из БД
      return {
        id,
        userId: user.sub,
        tourName: 'Desert Safari',
        tourDate: new Date(),
        numberOfPeople: 2,
        totalPrice: 500,
        status: 'CONFIRMED',
        createdAt: new Date(),
        updatedAt: new Date(),
      };
    },

    /**
     * Получить мои бронирования
     */
    myBookings: async (_, { status }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Получить из БД
      return [];
    },

    /**
     * Получить бронирования (для админов)
     */
    bookings: async (_, { userId, limit = 10 }, { user }) => {
      if (!user || user.role !== 'ADMIN') {
        throw new ApolloError('Access denied', 'FORBIDDEN');
      }

      // TODO: Получить из БД
      return [];
    },

    /**
     * Поиск бронирований
     */
    searchBookings: async (_, { tourName }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Поиск в БД
      return [];
    },
  },

  // ================ MUTATION ================

  Mutation: {
    /**
     * Создать бронирование
     */
    createBooking: async (_, { input }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // Валидация
      if (!input.tourName || !input.tourDate || !input.numberOfPeople) {
        throw new ApolloError('Missing required fields', 'INVALID_INPUT');
      }

      // TODO: Создать в БД
      return {
        id: Date.now().toString(),
        userId: user.sub,
        ...input,
        status: 'PENDING',
        createdAt: new Date(),
        updatedAt: new Date(),
      };
    },

    /**
     * Обновить бронирование
     */
    updateBooking: async (_, { id, input }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Проверить владельца бронирования
      // TODO: Обновить в БД

      return {
        id,
        userId: user.sub,
        tourName: 'Desert Safari',
        tourDate: new Date(),
        numberOfPeople: 2,
        totalPrice: 500,
        ...input,
        updatedAt: new Date(),
      };
    },

    /**
     * Отменить бронирование
     */
    cancelBooking: async (_, { id }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Отменить в БД

      return {
        id,
        status: 'CANCELLED',
        updatedAt: new Date(),
      };
    },

    /**
     * Обновить профиль
     */
    updateProfile: async (_, { name, email }, { user }) => {
      if (!user) {
        throw new ApolloError('Not authenticated', 'UNAUTHENTICATED');
      }

      // TODO: Обновить в БД

      return {
        id: user.sub,
        email: email || user.email,
        name: name || 'John Doe',
        role: user.role,
        createdAt: new Date(),
      };
    },
  },

  // ================ SUBSCRIPTION ================

  Subscription: {
    /**
     * Уведомление о новом бронировании
     */
    bookingCreated: {
      subscribe: (_, __, { pubsub }) => {
        return pubsub.asyncIterator(['BOOKING_CREATED']);
      },
    },

    /**
     * Обновление бронирования
     */
    bookingUpdated: {
      subscribe: (_, { bookingId }, { pubsub }) => {
        return pubsub.asyncIterator([`BOOKING_UPDATED_${bookingId}`]);
      },
    },
  },

  // ================ FIELD RESOLVERS ================

  Booking: {
    /**
     * Получить пользователя для бронирования
     */
    user: async (booking, _, { loaders }) => {
      // TODO: Использовать DataLoader для batch loading
      return {
        id: booking.userId,
        email: 'user@example.com',
        name: 'John Doe',
        role: 'USER',
      };
    },
  },

  User: {
    /**
     * Получить бронирования пользователя
     */
    bookings: async (user, _, { loaders }) => {
      // TODO: Получить из БД
      return [];
    },
  },

  // ================ SCALAR TYPES ================

  DateTime: {
    // Для серализации Date в ISO string
    serialize(value) {
      return value.toISOString();
    },
    // Для парсинга входящих данных
    parseValue(value) {
      return new Date(value);
    },
    // Для парсинга литерала в query
    parseLiteral(ast) {
      return new Date(ast.value);
    },
  },
};

// ==================== CONTEXT ====================

/**
 * Функция для создания context объекта
 * Вызывается для каждого request
 */
async function createContext({ req }) {
  // Получить user из JWT в header
  let user = null;

  try {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      // TODO: Проверить и декодировать токен
      user = {
        sub: '1',
        email: 'user@example.com',
        role: 'USER',
      };
    }
  } catch (error) {
    console.error('[GraphQL] Auth error:', error.message);
  }

  return {
    user,
    // TODO: Добавить DataLoader для batch loading
    // loaders: createLoaders(),
    // TODO: Добавить PubSub для subscriptions
    // pubsub: new PubSub(),
  };
}

module.exports = {
  typeDefs,
  resolvers,
  createContext,
};

// Usage в express приложении:
// const { ApolloServer } = require('apollo-server-express');
// const { typeDefs, resolvers, createContext } = require('./graphql-schema');
//
// const server = new ApolloServer({
//   typeDefs,
//   resolvers,
//   context: createContext,
// });
//
// await server.start();
// server.applyMiddleware({ app });
