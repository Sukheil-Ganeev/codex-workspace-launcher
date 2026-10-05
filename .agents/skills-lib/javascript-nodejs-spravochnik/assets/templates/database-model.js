/**
 * Database Model Template (Prisma/TypeORM)
 *
 * Production-ready шаблон для работы с БД.
 * Включает валидацию, hooks и методы для CRUD операций.
 *
 * @example
 * npm install @prisma/client
 * // или
 * npm install typeorm
 */

// ==================== PRISMA VERSION ====================

/**
 * Prisma schema (schema.prisma)
 *
 * model Booking {
 *   id            Int     @id @default(autoincrement())
 *   email         String  @unique
 *   phoneNumber   String
 *   tourDate      DateTime
 *   numberOfPeople Int
 *   status        String  @default("pending")
 *   notes         String?
 *   createdAt     DateTime @default(now())
 *   updatedAt     DateTime @updatedAt
 *
 *   @@index([email])
 *   @@index([status])
 * }
 */

// bookingModel.js
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

/**
 * Booking Model - CRUD операции
 */
class BookingModel {
  /**
   * Создать новое бронирование
   * @param {Object} data - Данные бронирования
   * @returns {Promise<Object>}
   */
  static async create(data) {
    // TODO: Добавить валидацию
    if (!data.email || !data.tourDate) {
      throw new Error('Email and tourDate are required');
    }

    try {
      const booking = await prisma.booking.create({
        data: {
          email: data.email.toLowerCase(),
          phoneNumber: data.phoneNumber,
          tourDate: new Date(data.tourDate),
          numberOfPeople: data.numberOfPeople || 1,
          notes: data.notes || null,
          status: 'pending',
        },
      });

      console.log(`[Booking] Created: ${booking.id}`);
      return booking;
    } catch (error) {
      if (error.code === 'P2002') {
        throw new Error('Email already exists');
      }
      throw error;
    }
  }

  /**
   * Получить бронирование по ID
   * @param {number} id
   * @returns {Promise<Object|null>}
   */
  static async findById(id) {
    return prisma.booking.findUnique({
      where: { id: parseInt(id) },
    });
  }

  /**
   * Получить все бронирования
   * @param {Object} options - { limit, skip, status }
   * @returns {Promise<Object[]>}
   */
  static async findAll(options = {}) {
    const { limit = 10, skip = 0, status } = options;

    const where = status ? { status } : {};

    return prisma.booking.findMany({
      where,
      take: limit,
      skip,
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * Обновить бронирование
   * @param {number} id
   * @param {Object} data - Данные для обновления
   * @returns {Promise<Object>}
   */
  static async update(id, data) {
    const booking = await prisma.booking.update({
      where: { id: parseInt(id) },
      data: {
        ...data,
        updatedAt: new Date(),
      },
    });

    console.log(`[Booking] Updated: ${booking.id}`);
    return booking;
  }

  /**
   * Удалить бронирование
   * @param {number} id
   * @returns {Promise<Object>}
   */
  static async delete(id) {
    const booking = await prisma.booking.delete({
      where: { id: parseInt(id) },
    });

    console.log(`[Booking] Deleted: ${booking.id}`);
    return booking;
  }

  /**
   * Получить статистику
   * @returns {Promise<Object>}
   */
  static async getStats() {
    const total = await prisma.booking.count();
    const byStatus = await prisma.booking.groupBy({
      by: ['status'],
      _count: {
        id: true,
      },
    });

    return {
      total,
      byStatus: Object.fromEntries(
        byStatus.map((item) => [item.status, item._count.id])
      ),
    };
  }
}

// ==================== TYPEORM VERSION ====================

/**
 * TypeORM Entity (если используется TypeORM)
 *
 * @Entity()
 * export class Booking {
 *   @PrimaryGeneratedColumn()
 *   id: number;
 *
 *   @Column({ unique: true })
 *   email: string;
 *
 *   @Column()
 *   phoneNumber: string;
 *
 *   @Column()
 *   tourDate: Date;
 *
 *   @Column({ default: 1 })
 *   numberOfPeople: number;
 *
 *   @Column({ nullable: true })
 *   notes: string;
 *
 *   @Column({ default: 'pending' })
 *   status: string;
 *
 *   @CreateDateColumn()
 *   createdAt: Date;
 *
 *   @UpdateDateColumn()
 *   updatedAt: Date;
 * }
 */

// ==================== EXPORTS ====================

module.exports = {
  BookingModel,
  // Добавить другие модели
};

// Cleanup on exit
process.on('exit', async () => {
  await prisma.$disconnect();
});
