//  Copyright (c) 2014 Thomas Heller
//
//  Distributed under the Boost Software License, Version 1.0. (See accompanying
//  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <hpx/hpx_main.hpp>
#include <hpx/hpx.hpp>
#include <hpx/runtime/parcelset/enable_disable.hpp>

#include <hpx/util/lightweight_test.hpp>

#include <boost/serialization/vector.hpp>

void f()
{}
HPX_PLAIN_ACTION(f);

std::size_t send_count()
{
    hpx::parcelset::connection_type conn
        = hpx::parcelset::connection_type::connection_mpi;
    return
        hpx::get_runtime().
            get_parcel_handler().
                get_parcel_send_count(conn, false);
}

std::size_t receive_count()
{
    hpx::parcelset::connection_type conn
        = hpx::parcelset::connection_type::connection_mpi;
    return
        hpx::get_runtime().
            get_parcel_handler().
                get_parcel_receive_count(conn, false);
}

void test_non_disabled(std::vector<hpx::id_type> const & localities)
{
    hpx::id_type here = hpx::find_here();

    std::size_t sent = send_count();
    std::size_t received = receive_count();
    
    std::vector<hpx::future<void> > futures;
    futures.reserve(localities.size());
    BOOST_FOREACH(hpx::id_type id, localities)
    {
        if(id != here)
            futures.push_back(hpx::async(f_action(), id));
    }
    hpx::this_thread::yield();
    hpx::wait_all(futures);

    if(sent != 0) HPX_TEST_NEQ(sent, send_count());
    if(sent != 0) HPX_TEST_NEQ(received, receive_count());
}

void test_disable_enable(std::vector<hpx::id_type> const & localities)
{
    hpx::id_type here = hpx::find_here();
    {
        hpx::parcelset::disable d;

        std::size_t sent = send_count();
        std::size_t received = receive_count();
        
        std::vector<hpx::future<void> > futures;
        futures.reserve(localities.size());
        BOOST_FOREACH(hpx::id_type id, localities)
        {
            if(id != here)
                futures.push_back(hpx::async(f_action(), id));
        }
        hpx::this_thread::yield();

        HPX_TEST_EQ(sent, send_count());
        HPX_TEST_EQ(received, receive_count());

        hpx::this_thread::yield();
        BOOST_FOREACH(hpx::future<void> const & f, futures)
        {
            HPX_TEST(!f.is_ready());
        }
        {
            hpx::parcelset::enable e(d);
            hpx::wait_all(futures);

            if(sent != 0) HPX_TEST_NEQ(sent, send_count());
            if(sent != 0) HPX_TEST_NEQ(received, receive_count());
        }
    }
}

void test_disable(std::vector<hpx::id_type> const & localities)
{
    hpx::id_type here = hpx::find_here();
    std::size_t sent = 0;
    std::size_t received = 0;
    std::vector<hpx::future<void> > futures;
    futures.reserve(localities.size());
    {
        hpx::parcelset::disable d;

        sent = send_count();
        received = receive_count();
        
        BOOST_FOREACH(hpx::id_type id, localities)
        {
            if(id != here)
                futures.push_back(hpx::async(f_action(), id));
        }
        hpx::this_thread::yield();

        HPX_TEST_EQ(sent, send_count());
        HPX_TEST_EQ(received, receive_count());

        hpx::this_thread::yield();
        BOOST_FOREACH(hpx::future<void> const & f, futures)
        {
            HPX_TEST(!f.is_ready());
        }
    }
    hpx::this_thread::yield();
    hpx::wait_all(futures);

    if(sent != 0) HPX_TEST_NEQ(sent, send_count());
    if(sent != 0) HPX_TEST_NEQ(received, receive_count());
}

void test(std::vector<hpx::id_type> const & localities)
{
    hpx::id_type here = hpx::find_here();
    // See if we are receiving/sending ok
    test_non_disabled(localities);
    // See if disabling/enabling works
    test_disable_enable(localities);
    // See if only disabling works
    test_disable(localities);
    // See if we are receiving/sending ok again
    test_non_disabled(localities);
}

HPX_PLAIN_ACTION(test);

int main()
{
    std::vector<hpx::id_type> localities = hpx::find_all_localities();

    test(localities);
    std::vector<hpx::future<void> > futures;
    futures.reserve(localities.size());
    BOOST_FOREACH(hpx::id_type id, localities)
    {
        futures.push_back(
            hpx::async(test_action(), id, localities)
        );
    }

    hpx::wait_all(futures);

    return hpx::util::report_errors();
}
