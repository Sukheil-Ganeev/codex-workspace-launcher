/**
 * GraphQL Query Template
 * Шаблон для выполнения GraphQL запросов
 *
 * Использование:
 *   node graphql_query.js
 */

// ============= Configuration =============

const GRAPHQL_ENDPOINT = process.env.GRAPHQL_ENDPOINT || 'https://api.example.com/graphql';
const API_KEY = process.env.API_KEY || 'your_api_key';

// ============= GraphQL Client =============

async function graphqlRequest(query, variables = {}) {
    const response = await fetch(GRAPHQL_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`
        },
        body: JSON.stringify({ query, variables })
    });

    const result = await response.json();

    if (result.errors) {
        console.error('GraphQL Errors:', result.errors);
        throw new Error(result.errors[0].message);
    }

    return result.data;
}

// ============= Example Queries =============

// Получить список туров
const GET_TOURS = `
    query GetTours($city: String!, $limit: Int) {
        tours(city: $city, limit: $limit) {
            id
            name
            description
            price
            currency
            duration
            available
            rating
            reviews {
                count
                average
            }
        }
    }
`;

// Получить детали тура
const GET_TOUR_DETAILS = `
    query GetTourDetails($tourId: ID!) {
        tour(id: $tourId) {
            id
            name
            description
            fullDescription
            price
            currency
            duration
            included
            excluded
            meetingPoint {
                address
                lat
                lng
            }
            photos {
                url
                caption
            }
            availability {
                date
                slots
            }
        }
    }
`;

// ============= Example Mutations =============

// Создать бронирование
const CREATE_BOOKING = `
    mutation CreateBooking($input: BookingInput!) {
        createBooking(input: $input) {
            id
            status
            totalPrice
            currency
            confirmationCode
            tour {
                name
            }
            customer {
                name
                email
            }
        }
    }
`;

// Отменить бронирование
const CANCEL_BOOKING = `
    mutation CancelBooking($bookingId: ID!, $reason: String) {
        cancelBooking(id: $bookingId, reason: $reason) {
            id
            status
            refundAmount
        }
    }
`;

// ============= Usage Examples =============

async function main() {
    try {
        // Пример 1: Получить туры в Дубае
        console.log('Fetching tours in Dubai...');
        const tours = await graphqlRequest(GET_TOURS, {
            city: 'dubai',
            limit: 10
        });
        console.log('Tours:', JSON.stringify(tours, null, 2));

        // Пример 2: Получить детали тура
        if (tours.tours && tours.tours.length > 0) {
            const tourId = tours.tours[0].id;
            console.log(`\nFetching details for tour ${tourId}...`);
            const tourDetails = await graphqlRequest(GET_TOUR_DETAILS, { tourId });
            console.log('Tour Details:', JSON.stringify(tourDetails, null, 2));
        }

        // Пример 3: Создать бронирование
        console.log('\nCreating booking...');
        const booking = await graphqlRequest(CREATE_BOOKING, {
            input: {
                tourId: 'tour-123',
                date: '2026-03-15',
                adults: 2,
                children: 1,
                customer: {
                    name: 'Иван Иванов',
                    email: 'ivan@example.com',
                    phone: '+971501234567'
                }
            }
        });
        console.log('Booking:', JSON.stringify(booking, null, 2));

    } catch (error) {
        console.error('Error:', error.message);
    }
}

// ============= Helper Functions =============

/**
 * Пагинация для больших списков
 */
async function fetchAllTours(city, pageSize = 20) {
    const ALL_TOURS_PAGINATED = `
        query GetAllTours($city: String!, $first: Int!, $after: String) {
            tours(city: $city, first: $first, after: $after) {
                edges {
                    node {
                        id
                        name
                        price
                    }
                    cursor
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    `;

    let allTours = [];
    let hasNextPage = true;
    let cursor = null;

    while (hasNextPage) {
        const result = await graphqlRequest(ALL_TOURS_PAGINATED, {
            city,
            first: pageSize,
            after: cursor
        });

        const edges = result.tours.edges;
        allTours = allTours.concat(edges.map(e => e.node));

        hasNextPage = result.tours.pageInfo.hasNextPage;
        cursor = result.tours.pageInfo.endCursor;

        console.log(`Fetched ${allTours.length} tours...`);
    }

    return allTours;
}

/**
 * Batch запросы для нескольких туров
 */
async function fetchMultipleTours(tourIds) {
    // GraphQL позволяет делать несколько запросов в одном
    const queries = tourIds.map((id, i) => `
        tour${i}: tour(id: "${id}") {
            id
            name
            price
        }
    `).join('\n');

    const query = `query { ${queries} }`;
    return await graphqlRequest(query);
}

// Export для использования как модуль
module.exports = {
    graphqlRequest,
    GET_TOURS,
    GET_TOUR_DETAILS,
    CREATE_BOOKING,
    CANCEL_BOOKING,
    fetchAllTours,
    fetchMultipleTours
};

// Запуск если вызван напрямую
if (require.main === module) {
    main();
}
